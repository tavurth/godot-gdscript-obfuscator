tool
extends Node

func _input(event: InputEvent):
	if not event is InputEventKey:
		return
	if not event.pressed:
		return

	if event.is_action_pressed("debug_orphans"):
		print_stray_nodes()


func test():
	"""
	This is a header comment
	This is a header comment
	This is a header comment
	"""

	#
	# This is a comment
	## This is a comment
	var a = 5
	if a > 5:
		print("HERE")
	else:
		print("NOT HERE")

	while true:
		if a > 5:
			continue


	match a:
		5:
			print("HERE")
		10:
			print("Not HERE")
		_:
			print("Not HERE")

	a = 10
