from celery import Celery

app = Celery('tasks', broker='mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0')

@app.task
def perform_search(image_to_search):
    # Your search function implementation here
    pass