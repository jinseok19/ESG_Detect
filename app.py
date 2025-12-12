import os
import traceback

from flask import Flask, render_template, request, redirect, flash, send_from_directory
from dotenv import load_dotenv
from rag_engine import ESG_RAG

# 환경변수 로드
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'esg-secret-key-2024'  # flash 메시지를 위한 시크릿 키
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('파일이 선택되지 않았습니다.', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('파일이 선택되지 않았습니다.', 'error')
                return redirect(request.url)
            
            # 파일 확장자 확인
            if not file.filename.lower().endswith('.pdf'):
                flash('PDF 파일만 업로드 가능합니다.', 'error')
                return redirect(request.url)
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                flash('OPENAI_API_KEY 환경변수가 설정되지 않았습니다.', 'error')
                return redirect(request.url)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # 파일 크기 체크 (100MB 제한 - 2GB 인스턴스)
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            if file_size > 100:
                flash(f'PDF 파일이 너무 큽니다 ({file_size:.1f}MB). 100MB 이하의 파일만 처리 가능합니다.', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            
            app.logger.info(f"PDF 파일 처리 시작: {file.filename} ({file_size:.1f}MB)")
            
            # RAG 엔진 초기화 (시간이 조금 걸릴 수 있음)
            try:
                rag = ESG_RAG(filepath, api_key)
            except MemoryError as e:
                flash(f'PDF 파일이 너무 크거나 복잡하여 메모리 부족이 발생했습니다. 더 작은 파일로 시도해주세요. ({str(e)})', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            except Exception as e:
                flash(f'PDF 파일 처리 중 오류가 발생했습니다: {str(e)}', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            
            # 검토할 ESG 항목 리스트 (확장)
            questions = {
                "scope1": {
                    "title": "Scope 1 배출량",
                    "question": "Scope 1 직접 배출량 데이터가 포함되어 있습니까? 있다면 구체적인 수치(단위 포함)와 연도를 알려주세요.",
                    "category": "환경"
                },
                "scope2": {
                    "title": "Scope 2 배출량",
                    "question": "Scope 2 간접 배출량(전력 등) 데이터가 포함되어 있습니까? 있다면 구체적인 수치(단위 포함)와 연도를 알려주세요.",
                    "category": "환경"
                },
                "scope3": {
                    "title": "Scope 3 배출량",
                    "question": "Scope 3 기타 간접 배출량 데이터가 포함되어 있습니까? 있다면 구체적인 수치(단위 포함), 범주, 연도를 알려주세요.",
                    "category": "환경"
                },
                "methodology": {
                    "title": "측정 방법론",
                    "question": "온실가스 배출량 측정 방법론(GHG Protocol, ISO 14064 등)이 명시되어 있습니까? 어떤 방법론을 사용했는지 구체적으로 설명해주세요.",
                    "category": "환경"
                },
                "materiality": {
                    "title": "이중 중대성 평가",
                    "question": "이중 중대성(Double Materiality) 평가를 수행했다는 내용이 있습니까? 재무적 중대성과 영향 중대성을 모두 평가했는지 설명해주세요.",
                    "category": "거버넌스"
                },
                "target": {
                    "title": "탄소 중립 목표",
                    "question": "탄소 중립(Carbon Neutral) 또는 넷제로(Net Zero) 목표가 설정되어 있습니까? 목표 연도와 구체적인 계획을 알려주세요.",
                    "category": "환경"
                },
                "renewable": {
                    "title": "재생 에너지",
                    "question": "재생 에너지 사용 현황이나 목표가 포함되어 있습니까? 있다면 비율이나 용량을 알려주세요.",
                    "category": "환경"
                },
                "diversity": {
                    "title": "다양성 및 포용성",
                    "question": "성별 다양성, 이사회 다양성 등 ESG의 Social 측면에서 다양성 및 포용성(D&I) 관련 내용이 있습니까? 구체적인 수치가 있다면 포함해주세요.",
                    "category": "사회"
                },
                "supply_chain": {
                    "title": "공급망 관리",
                    "question": "공급망(Supply Chain) ESG 관리 정책이나 프로그램이 설명되어 있습니까? 구체적인 내용을 알려주세요.",
                    "category": "사회"
                },
                "governance": {
                    "title": "거버넌스 구조",
                    "question": "ESG 거버넌스 구조(전담 조직, 이사회 위원회 등)가 설명되어 있습니까? 어떤 조직 구조를 갖추고 있는지 알려주세요.",
                    "category": "거버넌스"
                }
            }
            
            results = {}
            total_items = len(questions)
            found_count = 0
            
            for key, item in questions.items():
                try:
                    answer, sources, page_numbers = rag.ask(item["question"])
                    # 답변에서 "찾을 수 없습니다"가 포함되어 있으면 없음으로 판단
                    is_found = "찾을 수 없습니다" not in answer and "없습니다" not in answer[:50]
                    if is_found:
                        found_count += 1
                    
                    results[key] = {
                        "title": item["title"],
                        "category": item["category"],
                        "answer": answer,
                        "sources": sources if sources else [],
                        "page_numbers": page_numbers if page_numbers else [],  # 숫자 페이지 번호 리스트
                        "found": is_found
                    }
                except Exception as e:
                    results[key] = {
                        "title": item["title"],
                        "category": item["category"],
                        "answer": f"질문 처리 중 오류 발생: {str(e)}",
                        "sources": [],
                        "page_numbers": [],
                        "found": False
                    }
            
            # 전체 요약 생성
            summary = {
                "total": total_items,
                "found": found_count,
                "missing": total_items - found_count,
                "completion_rate": round((found_count / total_items) * 100, 1) if total_items > 0 else 0
            }
            
            return render_template('result.html', 
                                 results=results, 
                                 filename=file.filename,
                                 summary=summary,
                                 pdf_filename=file.filename)
            
        except Exception as e:
            error_msg = f'처리 중 오류가 발생했습니다: {str(e)}\n{traceback.format_exc()}'
            flash(error_msg, 'error')
            app.logger.error(error_msg)
            return redirect(request.url)
            
    return render_template('index.html')

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    """PDF 파일을 제공하는 엔드포인트"""
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            mimetype='application/pdf',
            as_attachment=False  # 브라우저에서 바로 열 수 있도록
        )
    except FileNotFoundError:
        flash('PDF 파일을 찾을 수 없습니다.', 'error')
        return redirect('/')

@app.route('/viewer/<filename>')
def pdf_viewer(filename):
    """PDF 뷰어 페이지 (페이지 번호 파라미터 지원)"""
    page = request.args.get('page', '1')
    highlight = request.args.get('q', '')
    return render_template('pdf_viewer.html', filename=filename, page=page, highlight=highlight)

if __name__ == '__main__':
    app.run(debug=True)
