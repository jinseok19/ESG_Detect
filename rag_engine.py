import os

from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class ESG_RAG:
    def __init__(self, pdf_path, api_key):
        self.pdf_path = pdf_path
        self.api_key = api_key
        self.vector_store = None
        self._initialize_vector_db()

    def _initialize_vector_db(self):
        """PDF를 로드하고 청크로 나누어 벡터 DB(FAISS)에 저장"""
        # 1. PDF 로드 (PDFPlumber 사용)
        loader = PDFPlumberLoader(self.pdf_path)
        documents = loader.load()
        
        if not documents:
            raise ValueError(f"PDF 파일에서 텍스트를 추출할 수 없습니다: {self.pdf_path}")
        
        # 페이지 메타데이터 정리 (PDFPlumber는 'page' 키 사용)
        for doc in documents:
            if 'page' in doc.metadata:
                doc.metadata['page_label'] = doc.metadata['page'] + 1  # 0-based를 1-based로 변환
            # 텍스트가 너무 짧으면 스킵 (빈 페이지나 이미지만 있는 페이지)
            if len(doc.page_content.strip()) < 50:
                continue

        # 2. 텍스트 분할 (Chunking)
        # 문맥이 끊기지 않도록 더 큰 청크로 설정 (한글은 더 많은 토큰 필요)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            length_function=len
        )
        texts = text_splitter.split_documents(documents)
        
        # 청크에도 페이지 메타데이터 유지
        for text in texts:
            if 'page' in text.metadata and 'page_label' not in text.metadata:
                text.metadata['page_label'] = text.metadata['page'] + 1

        # 3. 임베딩 및 벡터 저장소 생성
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.api_key
        )
        self.vector_store = FAISS.from_documents(texts, embeddings)

    def ask(self, question):
        """질문에 대해 근거를 찾아 답변"""
        
        # 상세하고 구조화된 답변을 위한 프롬프트
        prompt_template = """
        당신은 전문 ESG 규제 검토관입니다. 아래 [Context]에 제공된 내용을 바탕으로 질문에 상세하고 구체적으로 답하십시오.

        답변 작성 지침:
        1. [Context]에서 질문과 관련된 모든 정보를 찾아 종합적으로 답변하세요.
        2. 수치, 날짜, 단위, 방법론, 기준, 목표 등 구체적 정보가 있으면 반드시 포함하세요.
        3. 관련 키워드나 유사 표현이 사용된 경우도 포함하세요 (예: Scope 3 = 범위 3, GHG Protocol = 온실가스 프로토콜).
        4. 여러 페이지에 걸쳐 정보가 있으면 모두 종합하여 답변하세요.
        5. 수치나 데이터가 있다면: "XX tCO2eq (연도: YYYY)" 형식으로 명확히 표시하세요.
        6. 방법론이 언급되면: "GHG Protocol의 Scope 3 Guidance를 적용하여..."처럼 구체적으로 설명하세요.
        7. [Context]에 정말로 관련 내용이 전혀 없을 때만 "보고서에서 해당 내용을 찾을 수 없습니다"라고 답하세요.
        8. 답변은 2-4문장으로 간결하되 구체적으로 작성하세요.

        [Context]:
        {context}

        [Question]:
        {question}

        [Answer]:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        # RAG 체인 생성 (더 많은 청크 검색으로 포괄적 분석)
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=self.api_key),
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 8}  # 관련성 높은 문단 8개 참조 (더 포괄적)
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        result = qa_chain.invoke({"query": question})
        
        # 답변과 근거(페이지 번호) 추출
        answer = result['result']
        # 페이지 메타데이터에서 여러 키 시도
        sources = []
        for doc in result['source_documents']:
            page_num = None
            # page_label 우선 확인
            if 'page_label' in doc.metadata:
                page_num = doc.metadata['page_label']
            # page 키 확인 (0-based를 1-based로 변환)
            elif 'page' in doc.metadata:
                page_num = doc.metadata['page'] + 1
            # page_number 확인
            elif 'page_number' in doc.metadata:
                page_num = doc.metadata['page_number']
            
            if page_num:
                sources.append(f"{page_num}페이지")
            else:
                sources.append("Unknown페이지")
        unique_sources = list(set(sources))
        return answer, unique_sources
