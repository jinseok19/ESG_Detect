import os
import gc
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
import PyPDF2

class ESG_RAG:
    def __init__(self, pdf_path, api_key):
        self.pdf_path = pdf_path
        self.api_key = api_key
        self.vector_store = None
        self._initialize_vector_db()

    def _initialize_vector_db(self):
        """PDF를 로드하고 청크로 나누어 벡터 DB(FAISS)에 저장"""
        # 1. PDF 로드 (PyPDF2 사용 - 빠르고 메모리 효율적)
        documents = []
        
        # 최대 페이지 수 제한 (메모리/시간 절약)
        MAX_PAGES = 300  # 2GB 인스턴스에서 충분히 처리 가능
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                pages_to_process = min(total_pages, MAX_PAGES)
                
                if total_pages > MAX_PAGES:
                    logging.warning(f"PDF가 너무 큽니다 ({total_pages}페이지). 처음 {MAX_PAGES}페이지만 처리합니다.")
                else:
                    logging.info(f"PDF 총 {total_pages}페이지 처리 시작")
                
                for page_num in range(pages_to_process):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text and len(text.strip()) >= 50:
                            documents.append(Document(
                                page_content=text,
                                metadata={'page': page_num, 'page_label': page_num + 1}
                            ))
                        
                        # 20페이지마다 로깅 (2GB면 덜 자주 gc 필요)
                        if (page_num + 1) % 20 == 0:
                            gc.collect()
                            logging.info(f"{page_num + 1}/{pages_to_process} 페이지 처리 완료")
                            
                    except Exception as page_error:
                        logging.warning(f"페이지 {page_num + 1} 처리 중 오류: {str(page_error)}")
                        continue
                        
        except MemoryError:
            raise MemoryError("PDF 로드 중 메모리 부족. 파일이 너무 크거나 복잡할 수 있습니다.")
        except Exception as e:
            raise ValueError(f"PDF 파일 읽기 실패: {str(e)}")
        
        if not documents:
            raise ValueError(f"PDF 파일에서 텍스트를 추출할 수 없습니다: {self.pdf_path}")
        
        logging.info(f"총 {len(documents)}개 페이지에서 텍스트 추출 완료")

        # 2. 텍스트 분할 (Chunking)
        # 적절한 청크 크기로 품질 유지
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # 원래대로 복원 (2GB면 충분)
            chunk_overlap=300,
            length_function=len
        )
        
        logging.info("텍스트 분할 시작")
        texts = text_splitter.split_documents(documents)
        
        # 원본 documents 메모리 해제
        del documents
        gc.collect()
        
        # 청크에도 페이지 메타데이터 유지
        for text in texts:
            if 'page' in text.metadata and 'page_label' not in text.metadata:
                text.metadata['page_label'] = text.metadata['page'] + 1

        # 3. 임베딩 및 벡터 저장소 생성
        logging.info(f"임베딩 생성 시작 ({len(texts)}개 청크)")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.api_key
        )
        self.vector_store = FAISS.from_documents(texts, embeddings)
        
        logging.info("벡터 DB 생성 완료")
        
        # texts 메모리 해제
        del texts
        gc.collect()

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
        # RAG 체인 생성
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                model="gpt-4o", 
                temperature=0, 
                openai_api_key=self.api_key,
                request_timeout=60  # OpenAI API 타임아웃 설정 (60초)
            ),
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 8}  # 원래대로 복원 (더 포괄적 검색)
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        result = qa_chain.invoke({"query": question})
        
        # 답변과 근거(페이지 번호) 추출
        answer = result['result']
        # 페이지 메타데이터에서 여러 키 시도
        sources = []
        source_pages = []  # 숫자 페이지 번호 리스트
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
            
            if page_num and isinstance(page_num, (int, float)):
                page_num = int(page_num)
                sources.append(f"{page_num}페이지")
                source_pages.append(page_num)
            else:
                sources.append("Unknown페이지")
        unique_sources = list(set(sources))
        unique_pages = sorted(list(set(source_pages)))  # 숫자 페이지 번호 리스트 (중복 제거, 정렬)
        return answer, unique_sources, unique_pages
