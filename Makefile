.PHONY: investor-demo

investor-demo:
	@echo "Opening DreamCo investor demo..."
	@python3 -m webbrowser "file://$(PWD)/docs/investor_demo/index.html" || \
		(echo "Open docs/investor_demo/index.html manually." && exit 0)
