from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
import sys
from io import BytesIO
from base64 import b64encode
from PIL import Image
from matplotlib import pyplot as plt
from pathlib import Path

from fastai.basic_train import load_learner
from fastai.vision import SegmentationItemList, SegmentationLabelList, open_mask, open_image


export_file_name = 'export.pkl'

# Define the custom classes used by the learner
class SegLabelListCustom(SegmentationLabelList):
    def open(self, fn): return open_mask(fn, div=True)
    
class SegItemListCustom(SegmentationItemList):
    _label_cls = SegLabelListCustom

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def setup_learner():
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))

    # Run inference on the trained learner and base64 encode the result
    fig, ax = plt.subplots()
    img.show(ax, y=learn.predict(img)[0], alpha=0.6)
    resultPath = path/'static/result.png'
    fig.savefig(resultPath, bbox_inches='tight', pad_inches=0, transparent=True)

    return JSONResponse({'resultURL': 'static/' + resultPath.name})

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)
