import os
import json
import time
import sys
import pika
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the parent/backend directory to sys.path so we can import from main/setup_db/etc.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from setup_db import Task
from main import run_real_llm_agent, simulate_agentic_workflow, gateway
from auth import current_user_role, current_user_email

def process_task(ch, method, properties, body):
    try:
        payload = json.loads(body.decode('utf-8'))
        task_id = payload.get("task_id")
        query = payload.get("query")
        role = payload.get("role")
        email = payload.get("email")
        
        print(f"[Worker] Received task {task_id}: '{query}' for {email} ({role})", flush=True)
        
        # Set database session
        Session = sessionmaker(bind=gateway.engine)
        db = Session()
        
        # Update status to processing
        task_db = db.query(Task).filter(Task.task_id == task_id).first()
        if task_db:
            task_db.status = "processing"
            db.commit()
            
        # Set context variables for this execution
        token_role = current_user_role.set(role)
        token_email = current_user_email.set(email)
        
        try:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            custom_id = os.getenv("CUSTOM_CLIENT_ID")
            custom_secret = os.getenv("CUSTOM_CLIENT_SECRET")
            
            if (custom_id and custom_secret) or api_key:
                try:
                    result = run_real_llm_agent(query, role=role, email=email)
                except Exception as llm_err:
                    print(f"[Worker] Real LLM agent failed: {llm_err}. Falling back to simulator.", flush=True)
                    result = simulate_agentic_workflow(query, role=role, email=email)
            else:
                result = simulate_agentic_workflow(query, role=role, email=email)
            
            # Save success results
            task_db = db.query(Task).filter(Task.task_id == task_id).first()
            if task_db:
                task_db.status = "completed"
                task_db.result_json = json.dumps(result)
                task_db.finished_at = datetime.utcnow()
                db.commit()
                print(f"[Worker] Task {task_id} completed successfully.", flush=True)
                
        except Exception as err:
            print(f"[Worker] Error executing task {task_id}: {err}", flush=True)
            task_db = db.query(Task).filter(Task.task_id == task_id).first()
            if task_db:
                task_db.status = "failed"
                task_db.result_json = json.dumps({"error": str(err)})
                task_db.finished_at = datetime.utcnow()
                db.commit()
        finally:
            # Clean up context vars and DB session
            current_user_role.reset(token_role)
            current_user_email.reset(token_email)
            db.close()
            
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"[Worker] Error parsing or processing message: {e}", flush=True)
        # Nack the message if it failed in setup, but don't requeue to avoid poison pill loops
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception:
            pass

def main():
    print("[Worker] OmniGate ERP Background Worker starting...", flush=True)
    
    rabbitmq_conn_str = os.getenv("ConnectionStrings__rabbitmq")
    qdrant_conn_str = os.getenv("ConnectionStrings__qdrant")
    neo4j_conn_str = os.getenv("ConnectionStrings__neo4j")
    
    print(f"[Worker] RabbitMQ connection string: {rabbitmq_conn_str}", flush=True)
    print(f"[Worker] Qdrant connection string: {qdrant_conn_str}", flush=True)
    print(f"[Worker] Neo4j connection string: {neo4j_conn_str}", flush=True)
    
    if rabbitmq_conn_str:
        params = pika.URLParameters(rabbitmq_conn_str)
    else:
        params = pika.ConnectionParameters(host='localhost')
        
    while True:
        try:
            print("[Worker] Connecting to RabbitMQ...", flush=True)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.queue_declare(queue='agent_tasks', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='agent_tasks', on_message_callback=process_task)
            
            print("[Worker] Connected! Waiting for messages. To exit press CTRL+C", flush=True)
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as conn_err:
            print(f"[Worker] Connection failed: {conn_err}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)
        except KeyboardInterrupt:
            print("[Worker] Stopping background worker gracefully...", flush=True)
            break
        except Exception as e:
            print(f"[Worker] Unexpected worker error: {e}. Reconnecting in 5 seconds...", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
