from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    MANUFACTURER_DATASHEET = "manufacturer_datasheet"
    BUYER_FORM = "buyer_form"
    CALL_NOTES = "call_notes"

class SourceDefinition(BaseModel):
    id: str
    type: SourceType
    title: str
    location: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

BUYER_FORM_CONTENT = """Ref: INT-2024-8841
Buyer: SunBridge Trading Pvt. Ltd.
Destination: Bangladesh
Item: SUN-5K-G06P3-EU-AM2-P1 — buyer wrote "5000 W", rooftop
Maker: Ningbo Deye Inverter Technology Co., Ltd., China
Attached docs: none
Need by: 2024-11-30"""

CALL_NOTES_CONTENT = """Call notes from Ramesh, 2024-10-03:
Model SUN-5K-G06P3, 5 kW, Deye (China).
Said IP65.
Weight maybe 18 kg? Installer guessed.
Mentioned SGS and "high 90s efficiency" on the phone — nothing in writing.
No label photo yet.
They want something to circulate internally before the real certificates arrive.
OK to mark parts as "pending from factory" where unsure."""

def get_all_sources(datasheet_url: str) -> List[SourceDefinition]:
    return [
        SourceDefinition(
            id="source_1",
            type=SourceType.MANUFACTURER_DATASHEET,
            title="Manufacturer Datasheet (Deye SUN-4-12K-G06P3-EU-AM2-P1)",
            location=datasheet_url,
            metadata={"maker": "Ningbo Deye Inverter Technology Co., Ltd."}
        ),
        SourceDefinition(
            id="source_2",
            type=SourceType.BUYER_FORM,
            title="Buyer Purchase Inquiry Form (Ref: INT-2024-8841)",
            location="Buyer Form System",
            content=BUYER_FORM_CONTENT,
            metadata={
                "ref": "INT-2024-8841",
                "buyer": "SunBridge Trading Pvt. Ltd.",
                "destination": "Bangladesh",
                "need_by": "2024-11-30"
            }
        ),
        SourceDefinition(
            id="source_3",
            type=SourceType.CALL_NOTES,
            title="Call Notes from Ramesh (2024-10-03)",
            location="Call Note Registry",
            content=CALL_NOTES_CONTENT,
            metadata={
                "caller": "Ramesh",
                "date": "2024-10-03"
            }
        )
    ]
