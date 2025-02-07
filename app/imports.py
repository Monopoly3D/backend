from app.assets.objects.fields.casino import Casino
from app.assets.objects.fields.chance import Chance
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.police import Police
from app.assets.objects.fields.prison import Prison
from app.assets.objects.fields.start import Start
from app.assets.objects.fields.tax import Tax


def import_required_assets() -> None:
    Company.__subclasses__()
    Chance.__subclasses__()
    Start.__subclasses__()
    Tax.__subclasses__()
    Prison.__subclasses__()
    Police.__subclasses__()
    Casino.__subclasses__()
