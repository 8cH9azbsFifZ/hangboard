import boards

bb = Boards(boardname="zlagboard_evo")
bb.set_active_holds(["A1", "A7"])
bb.get_all_holds()
bb.get_hold_for_type("JUG")
bb.get_hold_for_type("20mm")