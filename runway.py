import os
from runwayml import RunwayML, TaskFailedError
from dotenv import load_dotenv
load_dotenv()

client = RunwayML(api_key=os.environ.get("RUNWAYML_API_SECRET"))

try:
  task = client.text_to_image.create(
    model='gen4_image',
    ratio='1920:1080',
    prompt_text='@EiffelTower painted in the style of @StarryNight',
    reference_images=[{
      'uri': 'https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg',
      'tag': 'EiffelTower',
    },
    {
      'uri': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1513px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
      'tag': 'StarryNight',
    }],
  ).wait_for_task_output()

  print('Task complete:', task)
  print('Image URL', task.output[0])
except TaskFailedError as e:
  print('The image failed to generate.')
  print(e.task_details)