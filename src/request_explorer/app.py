import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(docs_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


TRACKERS = {}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/")
def create_tracker():
    tracker_uuid = uuid.uuid4().hex

    TRACKERS[tracker_uuid] = []
    return RedirectResponse(f"/trackers/{tracker_uuid}", status_code=303)


@app.get("/trackers/{tracker_uuid}")
def get_tracker(tracker_uuid: str, request: Request):
    tracker = TRACKERS.get(tracker_uuid)
    if tracker is None:
        return Response(status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="tracker.html.j2",
        context={
            "tracker_url": request.url_for("track", tracker_uuid=tracker_uuid),
            "tracker_info": tracker,
        },
    )


@app.get("/trackers/{tracker_uuid}/track")
@app.post("/trackers/{tracker_uuid}/track")
@app.patch("/trackers/{tracker_uuid}/track")
@app.put("/trackers/{tracker_uuid}/track")
@app.delete("/trackers/{tracker_uuid}/track")
async def track(tracker_uuid: str, request: Request):
    tracker = TRACKERS.get(tracker_uuid)
    if tracker is None:
        return Response(status_code=404)

    tracker.append(
        {
            "method": request.method,
            "headers": [
                [key.decode(), value.decode()] for key, value in request.headers.raw
            ],
            "body": (await request.body()).decode(),
        }
    )


@app.get("/get_intent")
def get_intent():
    return Response(
        status_code=302,
        headers={
            "location": "intent://re.notsosmart.dev/intent_redirect#Intent;scheme=com.amazon.mobile.shopping.web;package=com.amazon.mShop.android.shopping;S.browser_fallback_url=https%3A%2F%2Fwww.amazon.com%2Fmessage-us%3Fref_%3Dfs_mbrowser_hybrid_hub_mu%26amp%26paradigm%3Dforesight%26amp%26muClientName%3Dforesight%26amp%26mu_params%3D%257B%2522hubSushiSessionId%2522%253A%2522588ea97d-13b6-465b-ad86-8c12ea3a3508%2522%252C%2522intentId%2522%253A%2522general_issue_selection%2522%252C%2522CPSDeeplinkEventId%2522%253A%2522b30ec06e-be54-42ca-a3d6-9ea632497a89%2522%257D%26sig%3Df1d23246-40e0-40d3-a3ed-024a1256097f;end"
        },
    )


@app.get("/intent_redirect")
def intent_redirect():
    return "Redirect wasss success"
