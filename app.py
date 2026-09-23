"""TaskForge MVP. Запуск: python app.py (внешние библиотеки не нужны)."""
import json,mimetypes,re,uuid
from datetime import datetime,timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
RULES=[("Контекст и потребность",20,["context","need"]),("Данные и материалы",20,["data"]),("Ожидаемый результат",15,["expected_result"]),("Критерии успеха",15,["success_criteria"]),("Ограничения",10,["constraints"]),("Пользователи",10,["users"]),("Связь с бизнесом",10,["contact"])]
TEAMS=[
 {"id":"team-1","name":"Data Nomads","interests":["ритейл","аналитика"],"skills":["Python","ML","FastAPI"]},
 {"id":"team-2","name":"Qadam Lab","interests":["образование","доступность"],"skills":["UX","JavaScript","NLP"]},
 {"id":"team-3","name":"Green Pulse","interests":["экология","города"],"skills":["IoT","DataViz","Python"]},
 {"id":"team-4","name":"Finity","interests":["финтех","безопасность"],"skills":["React","Risk","API"]},
 {"id":"team-5","name":"Steppe Vision","interests":["CV","логистика"],"skills":["Computer Vision","Python","Mobile"]}]
def now():return datetime.now(timezone.utc).isoformat()
def uid(p):return f"{p}-{uuid.uuid4().hex[:8]}"
def enrich(t):
 score=0;breakdown=[];missing=[]
 for label,points,fields in RULES:
  earned=points if t.get("confirmed") and all(len(str(t.get(f,"")).strip())>=3 for f in fields) else 0
  score+=earned;breakdown.append({"label":label,"earned":earned,"max":points})
  if not earned:missing.append(label)
 t.update(score=score,breakdown=breakdown,missing=missing,readiness="priority" if score>=90 else "ready" if score>=70 else "workable" if score>=40 else "draft")
 return t
def task(id,title,industry,context,need,created_at,**x):
 t={"id":id,"title":title,"industry":industry,"context":context,"need":need,"users":"","data":"","constraints":"","expected_result":"","success_criteria":"","contact":"","confirmed":True,"published":True,"created_at":created_at,"proposals":[]};t.update(x);return enrich(t)
TASKS=[
 task("task-1","Сократить очереди в университетской столовой","Образование","В обед студенты ждут заказ до 25 минут, сотрудники не видят будущую нагрузку.","Нужен сервис предзаказа и прогнозирования нагрузки по времени.","2026-09-22T09:00:00+00:00",users="Студенты, преподаватели и сотрудники столовой.",data="История продаж за 6 месяцев, меню и расписание пар.",constraints="MVP без онлайн-оплаты; запуск за 4 недели.",expected_result="Веб-MVP предзаказа и панель прогноза нагрузки.",success_criteria="Среднее ожидание ниже 10 минут; 60% заказов вовремя.",contact="Менеджер столовой; консультация по средам."),
 task("task-2","Прогнозировать остатки скоропортящихся товаров","Ритейл","Магазины списывают свежие продукты из-за неточного ручного заказа.","Нужен прогноз спроса на 7 дней по товарным категориям.","2026-09-21T13:30:00+00:00",users="Управляющие магазинов и специалисты по закупкам.",data="Продажи, остатки, промо и списания по 12 магазинам за год.",constraints="Без персональных данных; запуск на обычном ноутбуке.",expected_result="Модель прогноза и рекомендации объёма заказа.",success_criteria="Ошибка ниже baseline минимум на 15%.",contact="Продуктовый аналитик; две консультации в неделю."),
 task("task-3","Карта переполненных контейнерных площадок","Экология","Жители сообщают о переполнении по разным каналам, заявки дублируются.","Нужно собирать сигналы на карте и расставлять приоритеты.","2026-09-20T08:15:00+00:00",users="Жители и диспетчеры службы вывоза.",data="Примеры обращений и координаты 80 площадок.",expected_result="Прототип карты с фильтром по срочности.",success_criteria="Критичные точки находятся меньше чем за 2 минуты.",contact="Координатор проекта, созвон раз в неделю."),
 task("task-4","Объяснять причины отклонения заявок на микрокредит","Финтех","Клиенты получают формальный отказ и повторяют заявку без изменений.","Нужно понятное объяснение без раскрытия закрытых правил скоринга.","2026-09-19T15:45:00+00:00",users="Клиенты приложения и специалисты поддержки.",expected_result="Прототип экрана и библиотека безопасных формулировок.",constraints="Без чувствительных признаков и раскрытия весов скоринга."),
 task("task-5","Навигация по доступным маршрутам внутри кампуса","Городская среда","Гостям сложно понять, какой вход доступен маломобильному человеку.","Нужна карта доступных входов и маршрутов.","2026-09-18T11:20:00+00:00",users="Маломобильные посетители и сопровождающие.")]
PROPOSALS=[
 (0,"proposal-1","team-2","Qadam Lab","PWA-предзаказ с временными слотами","Прототип, тест на одной точке, анализ очереди","3 недели"),
 (0,"proposal-2","team-1","Data Nomads","Прогноз нагрузки по расписанию и чекам","Анализ, baseline-модель, дашборд","4 недели"),
 (1,"proposal-3","team-1","Data Nomads","Иерархический прогноз по магазинам","Очистка, backtest, API прогноза","4 недели"),
 (2,"proposal-4","team-3","Green Pulse","Карта сигналов с приоритетом по времени","Карта, дедупликация, тест","3 недели"),
 (3,"proposal-5","team-4","Finity","Контролируемый генератор объяснений","Матрица причин, шаблоны, UX-тест","2 недели")]
for i,pid,tid,name,idea,plan,timeline in PROPOSALS:TASKS[i]["proposals"].append({"id":pid,"team_id":tid,"team_name":name,"idea":idea,"plan":plan,"timeline":timeline,"prototype":"https://example.com/demo","status":"pending","created_at":now()})

QUESTIONS={
 "need":("Что именно должно измениться после решения задачи?","Сформулируйте желаемое изменение"),"users":("Кто будет пользоваться результатом?","Роли или группы пользователей"),
 "data":("Какие данные, материалы или примеры вы предоставите?","Формат, объём и источник данных"),"expected_result":("Какой конкретный результат должна передать команда?","Прототип, модель, исследование или сервис"),
 "success_criteria":("По каким измеримым признакам вы примете решение?","Метрики или проверяемые условия"),"constraints":("Какие есть сроки, технологии или ограничения?","Срок, стек, запреты"),
 "contact":("Как команда сможет общаться с бизнесом?","Контакт и формат консультаций")}
def analyze(text):
 clean=re.sub(r"\s+"," ",text).strip();low=clean.lower();words=clean.split();title=" ".join(words[:9]).rstrip(".,;:!?")+("…" if len(words)>9 else "")
 industry="Другое"
 for name,marks in {"Образование":("университет","школ","студент","обуч"),"Ритейл":("магазин","товар","продаж"),"Финтех":("банк","кредит","финанс"),"Экология":("отход","мусор","эколог"),"Городская среда":("город","маршрут","транспорт","кампус")}.items():
  if any(m in low for m in marks):industry=name;break
 card={"title":title[:100],"industry":industry,"context":clean,"need":"","users":"","data":"","constraints":"","expected_result":"","success_criteria":"","contact":""}
 markers={"users":("для ","пользовател","клиент","сотрудник","студент"),"data":("данн","csv","таблиц","api"),"constraints":("срок","нельзя","огранич","недел"),"expected_result":("прототип","сервис","модель","приложение"),"success_criteria":("процент","%","метрик","сниз"),"contact":("контакт","созвон","консультац")}
 found={f for f,ms in markers.items() if any(m in low for m in ms)};order=["need","users","data","expected_result","success_criteria","constraints","contact"]
 missing=[f for f in order if f not in found]
 if len(missing)<3:missing += [f for f in order if f not in missing]
 return {"card":card,"questions":[{"field":f,"text":QUESTIONS[f][0],"placeholder":QUESTIONS[f][1]} for f in missing[:5]],"analysis":{"mode":"local-stub","invented_facts":False}}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,fmt,*args):print(f"[{self.log_date_time_string()}] {fmt%args}")
 def json(self,data,status=200):
  body=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body)
 def read(self):
  try:
   n=int(self.headers.get("Content-Length","0"));return json.loads(self.rfile.read(n).decode())
  except Exception:raise ValueError("Некорректный JSON")
 def do_GET(self):
  p=urlparse(self.path).path
  if p=="/api/bootstrap":return self.json({"tasks":sorted(TASKS,key=lambda x:x["score"],reverse=True),"teams":TEAMS})
  if p=="/api/tasks":return self.json(TASKS)
  self.static(p)
 def do_POST(self):
  p=urlparse(self.path).path
  try:d=self.read()
  except ValueError as e:return self.json({"error":str(e)},400)
  if p=="/api/analyze":
   text=str(d.get("description","")).strip()
   return self.json(analyze(text[:1200])) if len(text)>=12 else self.json({"error":"Описание должно содержать хотя бы 12 символов"},400)
  if p=="/api/tasks":return self.create_task(d)
  m=re.fullmatch(r"/api/tasks/([^/]+)/proposals",p)
  if m:return self.create_proposal(m.group(1),d)
  m=re.fullmatch(r"/api/proposals/([^/]+)/decision",p)
  if m:return self.decide(m.group(1),d)
  self.json({"error":"Маршрут не найден"},404)
 def create_task(self,d):
  if not all(str(d.get(x,"")).strip() for x in ("title","context","need")):return self.json({"error":"Нужны название, контекст и потребность"},400)
  if d.get("confirmed") is not True:return self.json({"error":"Подтвердите карточку"},400)
  fields=("title","industry","context","need","users","data","constraints","expected_result","success_criteria","contact");t={f:str(d.get(f,"")).strip()[:2000] for f in fields};t.update(id=uid("task"),title=t["title"][:100],industry=t["industry"] or "Другое",confirmed=True,published=True,created_at=now(),proposals=[]);enrich(t);TASKS.append(t);self.json(t,201)
 def create_proposal(self,tid,d):
  t=next((x for x in TASKS if x["id"]==tid),None);team=next((x for x in TEAMS if x["id"]==d.get("team_id")),None)
  if not t or not team:return self.json({"error":"Задача или команда не найдена"},404)
  if not all(str(d.get(x,"")).strip() for x in ("idea","plan","timeline")):return self.json({"error":"Заполните идею, план и срок"},400)
  p={"id":uid("proposal"),"team_id":team["id"],"team_name":team["name"],"idea":str(d["idea"])[:500],"plan":str(d["plan"])[:1000],"timeline":str(d["timeline"])[:100],"prototype":str(d.get("prototype",""))[:500],"status":"pending","created_at":now()};t["proposals"].append(p);self.json(p,201)
 def decide(self,pid,d):
  choice=d.get("decision")
  if choice not in ("selected","rejected"):return self.json({"error":"Можно выбрать или отклонить"},400)
  for t in TASKS:
   for p in t["proposals"]:
    if p["id"]==pid:p["status"]=choice;p["decided_at"]=now();return self.json(p)
  self.json({"error":"Отклик не найден"},404)
 def static(self,p):
  name="index.html" if p in ("","/") else p.lstrip("/");f=(ROOT/name).resolve()
  if f.parent!=ROOT or name not in ("index.html","styles.css","app.js") or not f.is_file():return self.send_error(404)
  body=f.read_bytes();self.send_response(200);self.send_header("Content-Type",(mimetypes.guess_type(name)[0] or "application/octet-stream")+"; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-cache");self.end_headers();self.wfile.write(body)
if __name__=="__main__":
 server=ThreadingHTTPServer(("127.0.0.1",8000),Handler);print("TaskForge: http://127.0.0.1:8000");print("Остановить: Ctrl+C")
 try:server.serve_forever()
 except KeyboardInterrupt:print("\nСервер остановлен")
 finally:server.server_close()
