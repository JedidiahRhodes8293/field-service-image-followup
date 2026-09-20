from field_service_images import dispatch_update


def test_saved_photo_moves_dispatch_to_follow_up() -> None:
    update = dispatch_update(True, "Mina")
    assert update.status == "follow_up_required"
    assert update.follow_up == "Mina review the generated site photo"


def test_missing_photo_keeps_dispatch_waiting() -> None:
    update = dispatch_update(False, "Mina")
    assert update.status == "awaiting_photo"
