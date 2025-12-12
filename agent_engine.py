"""
ESG-Radar Multi-Agent System
LangGraph 기반 3단계 검증 시스템:
1. Integrity Engine: 데이터 정합성 및 K-ESG 5대 항목 검증
2. Green Audit: 그린워싱 위험 탐지
3. Report Generator: 최종 점수 및 인증서 생성
"""

import os
import logging
from typing import TypedDict, Annotated, List, Dict
from operator import add

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from rag_engine import ESG_RAG


# State 정의
class ESGRadarState(TypedDict):
    """ESG-Radar 워크플로우 상태"""
    pdf_path: str
    api_key: str
    rag_engine: ESG_RAG
    
    # Integrity Engine 결과
    integrity_findings: Dict
    k_esg_checklist: Dict
    integrity_score: float
    decoupling_analysis: Dict
    
    # Green Audit 결과
    greenwashing_risks: List[Dict]
    greenwashing_score: float
    risk_level: str
    
    # 최종 리포트
    final_report: Dict
    pre_assurance_eligible: bool
    
    # 메시지 누적
    messages: Annotated[List[str], add]


class ESGRadarAgent:
    """ESG-Radar Multi-Agent 시스템"""
    
    def __init__(self, pdf_path: str, api_key: str):
        self.pdf_path = pdf_path
        self.api_key = api_key
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=api_key,
            request_timeout=90
        )
        
        # RAG 엔진 초기화
        self.rag = ESG_RAG(pdf_path, api_key)
        
        # StateGraph 구성
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """LangGraph workflow 구성"""
        workflow = StateGraph(ESGRadarState)
        
        # 노드 추가
        workflow.add_node("integrity_engine", self.integrity_engine_node)
        workflow.add_node("green_audit", self.green_audit_node)
        workflow.add_node("report_generator", self.report_generator_node)
        
        # 엣지 연결
        workflow.set_entry_point("integrity_engine")
        workflow.add_edge("integrity_engine", "green_audit")
        workflow.add_edge("green_audit", "report_generator")
        workflow.add_edge("report_generator", END)
        
        return workflow
    
    def integrity_engine_node(self, state: ESGRadarState) -> ESGRadarState:
        """
        Node 1: 데이터 정합성 검증 엔진
        - K-ESG 5대 필수 항목 체크
        - Decoupling 분석 (매출/생산량 대비 배출량 추이)
        - 교차 검증 로직
        """
        logging.info("🔍 Integrity Engine 시작...")
        
        # K-ESG 5대 필수 항목
        k_esg_items = {
            "ghg": {
                "title": "온실가스 배출량",
                "query": "Scope 1, 2, 3 온실가스 배출량이 모두 보고되어 있습니까? 각 Scope별 수치와 단위, 연도를 알려주세요."
            },
            "energy": {
                "title": "에너지 사용량",
                "query": "에너지 사용량(전력, 연료 등)과 재생에너지 비율이 보고되어 있습니까? 구체적인 수치를 알려주세요."
            },
            "water": {
                "title": "용수 사용량",
                "query": "용수 사용량과 용수 재활용률이 보고되어 있습니까? 구체적인 수치를 알려주세요."
            },
            "waste": {
                "title": "폐기물 발생량",
                "query": "폐기물 발생량과 재활용률이 보고되어 있습니까? 구체적인 수치를 알려주세요."
            },
            "compliance": {
                "title": "법규 위반 사항",
                "query": "환경 관련 법규 위반 사항이나 제재 이력이 보고되어 있습니까? 없다면 명시적으로 '없음'이라고 기재되어 있습니까?"
            }
        }
        
        # 각 항목 검증
        checklist_results = {}
        total_found = 0
        
        for key, item in k_esg_items.items():
            answer, sources, pages = self.rag.ask(item["query"])
            
            # 데이터 존재 여부 판단
            has_data = "찾을 수 없습니다" not in answer and "없습니다" not in answer[:30]
            if has_data:
                total_found += 1
            
            checklist_results[key] = {
                "title": item["title"],
                "found": has_data,
                "answer": answer,
                "sources": sources,
                "pages": pages
            }
        
        # Decoupling 분석
        decoupling_query = """
        매출액, 생산량 등 사업 성과와 온실가스 배출량, 에너지 사용량의 탈동조화(Decoupling) 추이가 설명되어 있습니까?
        예를 들어 '매출 증가에도 불구하고 배출량은 감소' 같은 설명이 있는지 확인하고, 
        구체적인 수치와 비교 연도를 알려주세요.
        """
        decoupling_answer, decoupling_sources, decoupling_pages = self.rag.ask(decoupling_query)
        
        has_decoupling = "찾을 수 없습니다" not in decoupling_answer and len(decoupling_answer) > 50
        
        decoupling_analysis = {
            "explained": has_decoupling,
            "answer": decoupling_answer,
            "sources": decoupling_sources,
            "pages": decoupling_pages
        }
        
        # 정합성 점수 계산 (0-100)
        base_score = (total_found / len(k_esg_items)) * 70  # 5대 항목: 70점
        decoupling_bonus = 30 if has_decoupling else 0  # Decoupling: 30점
        integrity_score = min(100, base_score + decoupling_bonus)
        
        state["k_esg_checklist"] = checklist_results
        state["decoupling_analysis"] = decoupling_analysis
        state["integrity_score"] = round(integrity_score, 1)
        state["integrity_findings"] = {
            "total_items": len(k_esg_items),
            "items_found": total_found,
            "completion_rate": round((total_found / len(k_esg_items)) * 100, 1)
        }
        state["messages"] = [f"✅ Integrity Engine 완료: {integrity_score}점"]
        
        logging.info(f"✅ Integrity Score: {integrity_score}점")
        return state
    
    def green_audit_node(self, state: ESGRadarState) -> ESGRadarState:
        """
        Node 2: 그린워싱 감지 엔진
        - 환경부 '환경성 표시·광고 관리제도' 위반 유형 검사
        - EU Green Claims Directive 핵심 기준 검증
        - 위험도 레벨 산정 (High/Medium/Low)
        """
        logging.info("🌱 Green Audit 시작...")
        
        # 그린워싱 탐지 지식베이스
        knowledge_base = """
        ## 주요 그린워싱 위반 유형 (환경부 고시 + EU Green Claims Directive)
        
        1. **모호한 표현 (Vague Claims)**
           - "친환경", "에코", "그린", "지속가능" 등 구체적 근거 없는 일반적 표현
           - 예: "친환경 제품입니다" (×) → "재활용 플라스틱 80% 사용" (○)
        
        2. **미래 목표의 근거 부재 (Unsubstantiated Future Claims)**
           - 2030/2050 탄소중립 선언만 있고 구체적 이행 계획, 중간 목표, 투자 계획 없음
           - 예: "2050 탄소중립 달성" (×) → "2030년까지 배출량 50% 감축, 재생에너지 전환 투자 5000억원" (○)
        
        3. **전 과정 평가 누락 (Cherry-picking)**
           - 제품 생산 단계만 강조하고 원료 채취, 운송, 폐기 단계의 환경영향은 누락
           - Scope 3 배출량 미공개
           - 예: "생산 과정에서 탄소 배출 제로" (Scope 1, 2만 언급하고 Scope 3 누락) (×)
        """
        
        # 그린워싱 위험 질문
        risk_queries = [
            {
                "category": "모호한 표현",
                "query": """
                '친환경', '에코', '그린', '지속가능' 등의 표현이 사용되는 곳에서 
                구체적인 수치적 근거(재활용률, 배출량 감축률, 인증 번호 등)가 함께 제시되어 있습니까?
                모호한 표현만 사용된 사례를 찾아주세요.
                """,
                "severity_if_found": "Medium"
            },
            {
                "category": "미래 목표 근거 부재",
                "query": """
                탄소중립, 넷제로 등 미래 목표가 언급되는 경우,
                구체적인 로드맵(연도별 중간 목표, 투자 금액, 기술 도입 계획)이 함께 제시되어 있습니까?
                목표만 있고 이행 계획이 없는 사례를 찾아주세요.
                """,
                "severity_if_found": "High"
            },
            {
                "category": "전 과정 평가 누락",
                "query": """
                환경 성과를 주장할 때 전 과정(원료-생산-유통-폐기)이 모두 다뤄지고 있습니까?
                특히 Scope 3 배출량이 보고되어 있습니까?
                일부 단계만 강조하고 다른 단계는 누락된 사례를 찾아주세요.
                """,
                "severity_if_found": "High"
            }
        ]
        
        # 각 위험 항목 검사
        risks_found = []
        risk_scores = []
        
        for risk_query in risk_queries:
            # 프롬프트 강화: 지식베이스 포함
            full_prompt = f"""
            {knowledge_base}
            
            위의 그린워싱 기준을 바탕으로 다음 질문에 답하세요:
            {risk_query['query']}
            
            위험 사례가 발견되면 구체적인 문구와 페이지 번호를 명시하고,
            발견되지 않으면 "위험 요소가 발견되지 않았습니다"라고 답하세요.
            """
            
            answer, sources, pages = self.rag.ask(full_prompt)
            
            # 위험 발견 여부 판단
            risk_detected = (
                "위험 요소가 발견되지 않았습니다" not in answer and
                "찾을 수 없습니다" not in answer and
                len(answer) > 50
            )
            
            if risk_detected:
                risk_item = {
                    "category": risk_query["category"],
                    "severity": risk_query["severity_if_found"],
                    "description": answer,
                    "sources": sources,
                    "pages": pages,
                    "regulation": "환경부 환경성 표시·광고 관리제도 / EU Green Claims Directive"
                }
                risks_found.append(risk_item)
                
                # 심각도별 감점
                if risk_query["severity_if_found"] == "High":
                    risk_scores.append(-30)
                elif risk_query["severity_if_found"] == "Medium":
                    risk_scores.append(-15)
                else:
                    risk_scores.append(-5)
        
        # 그린워싱 위험 점수 계산 (100점 만점, 위험 발견 시 감점)
        greenwashing_score = max(0, 100 + sum(risk_scores))
        
        # 위험 레벨 판정
        if greenwashing_score >= 80:
            risk_level = "Low"
        elif greenwashing_score >= 60:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        state["greenwashing_risks"] = risks_found
        state["greenwashing_score"] = round(greenwashing_score, 1)
        state["risk_level"] = risk_level
        state["messages"].append(f"✅ Green Audit 완료: {greenwashing_score}점 (위험도: {risk_level})")
        
        logging.info(f"✅ Greenwashing Score: {greenwashing_score}점 (위험도: {risk_level})")
        return state
    
    def report_generator_node(self, state: ESGRadarState) -> ESGRadarState:
        """
        Node 3: 최종 리포트 생성
        - 종합 점수 계산
        - Pre-Assurance 인증 자격 판정 (80점 이상)
        - 대시보드용 JSON 생성
        """
        logging.info("📊 Report Generator 시작...")
        
        integrity_score = state["integrity_score"]
        greenwashing_score = state["greenwashing_score"]
        
        # 종합 점수 (가중평균: 정합성 60%, 그린워싱 40%)
        composite_score = round(integrity_score * 0.6 + greenwashing_score * 0.4, 1)
        
        # Pre-Assurance 자격 판정
        pre_assurance_eligible = (
            integrity_score >= 80 and 
            greenwashing_score >= 80 and
            state["risk_level"] == "Low"
        )
        
        # 최종 리포트 구성
        final_report = {
            "composite_score": composite_score,
            "integrity_score": integrity_score,
            "greenwashing_score": greenwashing_score,
            "risk_level": state["risk_level"],
            "pre_assurance_eligible": pre_assurance_eligible,
            
            # 상세 정보
            "k_esg_checklist": state["k_esg_checklist"],
            "decoupling_analysis": state["decoupling_analysis"],
            "greenwashing_risks": state["greenwashing_risks"],
            
            # 메타데이터
            "pdf_path": state["pdf_path"],
            "total_risks_found": len(state["greenwashing_risks"]),
            "k_esg_completion": state["integrity_findings"]["completion_rate"]
        }
        
        state["final_report"] = final_report
        state["pre_assurance_eligible"] = pre_assurance_eligible
        state["messages"].append(f"✅ 최종 리포트 생성 완료 (종합: {composite_score}점)")
        
        logging.info(f"✅ 최종 종합 점수: {composite_score}점")
        if pre_assurance_eligible:
            logging.info("🏆 Pre-Assurance 인증 자격 획득!")
        
        return state
    
    def run(self) -> Dict:
        """워크플로우 실행"""
        initial_state = {
            "pdf_path": self.pdf_path,
            "api_key": self.api_key,
            "rag_engine": self.rag,
            "messages": []
        }
        
        # 워크플로우 실행
        final_state = self.app.invoke(initial_state)
        
        return final_state["final_report"]


def analyze_esg_report(pdf_path: str, api_key: str) -> Dict:
    """
    ESG 보고서 종합 분석 (진입점)
    
    Args:
        pdf_path: PDF 파일 경로
        api_key: OpenAI API 키
    
    Returns:
        최종 분석 리포트 (Dict)
    """
    agent = ESGRadarAgent(pdf_path, api_key)
    report = agent.run()
    return report

