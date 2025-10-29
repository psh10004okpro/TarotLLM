"""
Test script for Phase 2 - Comprehensive Tarot Database
"""

from app.services.rag_service import rag_service
from app.models.tarot_card import CardSuit

def test_card_loading():
    """Test that all 78 cards load correctly"""
    print("=" * 60)
    print("Phase 2 Test: Tarot Card Database")
    print("=" * 60)

    # Get statistics
    stats = rag_service.get_statistics()
    print("\n📊 Card Statistics:")
    print(f"   Total Cards: {stats['total_cards']}")
    print(f"   Major Arcana: {stats['major_arcana']}")
    print(f"   Wands: {stats['wands']}")
    print(f"   Cups: {stats['cups']}")
    print(f"   Swords: {stats['swords']}")
    print(f"   Pentacles: {stats['pentacles']}")

    # Verify total
    expected = 78
    actual = stats['total_cards']
    status = "✅ PASS" if actual == expected else f"❌ FAIL (expected {expected})"
    print(f"\n   Status: {status}")

    # Test card retrieval by ID
    print("\n" + "=" * 60)
    print("Testing Card Retrieval")
    print("=" * 60)

    # Test The Fool (0)
    fool = rag_service.get_card_by_id(0)
    if fool:
        print(f"\n✅ Card 0: {fool.name} ({fool.name_ko})")
        print(f"   Keywords: {', '.join(fool.keywords[:5])}...")
        print(f"   Suit: {fool.suit.value}")
    else:
        print("\n❌ Card 0 not found")

    # Test The World (21)
    world = rag_service.get_card_by_id(21)
    if world:
        print(f"\n✅ Card 21: {world.name} ({world.name_ko})")
        print(f"   Keywords: {', '.join(world.keywords[:5])}...")

    # Test Ace of Cups (22)
    ace_cups = rag_service.get_card_by_id(22)
    if ace_cups:
        print(f"\n✅ Card 22: {ace_cups.name} ({ace_cups.name_ko})")
        print(f"   Suit: {ace_cups.suit.value}")
        print(f"   Keywords: {', '.join(ace_cups.keywords[:5])}...")

    # Test context-specific meanings
    print("\n" + "=" * 60)
    print("Testing Context-Specific Interpretations")
    print("=" * 60)

    if fool:
        print("\n💕 Love interpretation:")
        print(f"   {fool.love[:100]}...")

        print("\n💰 Finance interpretation:")
        print(f"   {fool.finance[:100]}...")

        print("\n💼 Career interpretation:")
        print(f"   {fool.education_career_business[:100]}...")

    # Test search functionality
    print("\n" + "=" * 60)
    print("Testing Search Functionality")
    print("=" * 60)

    love_cards = rag_service.search_cards("연애")
    print(f"\n🔍 Cards matching '연애': {len(love_cards)} found")
    if love_cards:
        for card in love_cards[:3]:
            print(f"   - {card.name} ({card.name_ko})")

    # Test suit-based retrieval
    print("\n" + "=" * 60)
    print("Testing Suit-Based Retrieval")
    print("=" * 60)

    major_arcana = rag_service.get_cards_by_suit(CardSuit.MAJOR_ARCANA)
    wands = rag_service.get_cards_by_suit(CardSuit.WANDS)
    cups = rag_service.get_cards_by_suit(CardSuit.CUPS)

    print(f"\n🎴 Major Arcana: {len(major_arcana)} cards")
    if major_arcana:
        print(f"   First: {major_arcana[0].name}")
        print(f"   Last: {major_arcana[-1].name}")

    print(f"\n🔥 Wands: {len(wands)} cards")
    if wands:
        print(f"   First: {wands[0].name}")
        print(f"   Last: {wands[-1].name}")

    print(f"\n💧 Cups: {len(cups)} cards")
    if cups:
        print(f"   First: {cups[0].name}")
        print(f"   Last: {cups[-1].name}")

    # Test comprehensive card info
    print("\n" + "=" * 60)
    print("Testing Comprehensive Card Info")
    print("=" * 60)

    if fool:
        info = rag_service.get_comprehensive_card_info(0)
        print(f"\n📋 The Fool - Complete Info:")
        print(f"   ID: {info['id']}")
        print(f"   Name: {info['name']}")
        print(f"   Korean: {info['name_ko']}")
        print(f"   Suit: {info['suit']}")
        print(f"   Keywords: {len(info['keywords'])} keywords")
        print(f"   Has love interpretation: {'love' in info['interpretations'] and bool(info['interpretations']['love'])}")
        print(f"   Has symbolism: {bool(info['symbolic']['symbolism'])}")
        print(f"   Has advice: {bool(info['guidance']['advice'])}")

    print("\n" + "=" * 60)
    print("Phase 2 Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_card_loading()
