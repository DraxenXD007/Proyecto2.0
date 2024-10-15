from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from pydantic import BaseModel

router = APIRouter()

class LinkData(BaseModel):
    content: str

    def to_list(self):
        return [self.content]

@cbv(router)
class LinkScribeCbv:
    @router.post("/predict")
    async def predict(self, request: Request, data: LinkData):
        model_input = data.to_list()
        model_garden = request.app.state.model_garden
        model = model_garden["link-scribe-model"]
        predictions = model.predict([model_input])
        return JSONResponse(content={"prediction": predictions})
