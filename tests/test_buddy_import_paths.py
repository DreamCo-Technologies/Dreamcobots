from BuddyAI.buddy import Buddy


def test_buddy_registers_category_bots_from_package_paths():
    buddy = Buddy()

    assert "GovernmentContractGrantBot" in buddy.bots
    assert "AdministrativeSupportBot" in buddy.bots
    assert "BooksAppBot" in buddy.bots
    assert "AccommodationFoodBot" in buddy.bots
    assert len(buddy.bots) == 67

