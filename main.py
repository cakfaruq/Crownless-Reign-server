from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

# Dummy database player
players = {
    "CRX001": {
        "username": "Crownless",
        "weapon": {
            "name": "Ironborn Sword",
            "upgrade_level": 10,
            "glow": False
        },
        "inventory": {
            "sigil_protection": 1
        }
    }
}

# Request model
class UpgradeRequest(BaseModel):
    player_id: str
    item_type: str  # only 'weapon' supported for now
    use_sigil: bool = False

# Response model
class UpgradeResponse(BaseModel):
    success: bool
    new_upgrade_level: int = None
    glow: bool = False
    message: str

# Upgrade chance function
def calculate_upgrade_chance(level):
    if level <= 5:
        return 1.0
    elif level <= 10:
        return 0.85 - (level - 6) * 0.05
    elif level == 11:
        return 0.3
    elif level == 12:
        return 0.25
    elif level == 13:
        return 0.2
    elif level == 14:
        return 0.15
    elif level == 15:
        return 0.1
    return 0

@app.post("/upgrade", response_model=UpgradeResponse)
def upgrade_item(req: UpgradeRequest):
    player = players.get(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    item = player.get(req.item_type)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    level = item["upgrade_level"]
    if level >= 15:
        return UpgradeResponse(success=False, message="Max level reached")

    chance = calculate_upgrade_chance(level + 1)
    success = random.random() <= chance

    if success:
        item["upgrade_level"] += 1
        item["glow"] = item["upgrade_level"] >= 11
        return UpgradeResponse(
            success=True,
            new_upgrade_level=item["upgrade_level"],
            glow=item["glow"],
            message=f"Upgrade success! {item['name']} is now +{item['upgrade_level']}"
        )
    else:
        if level >= 11:
            if req.use_sigil and player["inventory"]["sigil_protection"] > 0:
                player["inventory"]["sigil_protection"] -= 1
                return UpgradeResponse(success=False, message="Upgrade failed but item protected by Sigil.")
            else:
                item["upgrade_level"] -= 1
                item["glow"] = item["upgrade_level"] >= 11
                return UpgradeResponse(success=False, message=f"Upgrade failed. Item downgraded to +{item['upgrade_level']}")
        return UpgradeResponse(success=False, message="Upgrade failed.")
from pydantic import BaseModel
from typing import Dict

# Simpan data player sementara (in-memory)
players_db: Dict[str, dict] = {}

class Player(BaseModel):
    player_id: str
    username: str

@app.post("/register")
def register_player(player: Player):
    if player.player_id in players_db:
        return {"message": "Player already registered"}
    players_db[player.player_id] = {
        "username": player.username
    }
    return {"message": "Player registered successfully", "player": player}
