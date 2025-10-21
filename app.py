from llmselect import create_app

app = create_app()

if __name__ == "__main__":
    port = int(app.config.get("PORT", 3044))
    app.run(host="0.0.0.0", port=port)
