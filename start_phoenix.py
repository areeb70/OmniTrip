import phoenix as px

print("Starting Phoenix Local Server...")
try:
    # This launches the server and the dashboard
    session = px.launch()
    print("\n" + "="*50)
    print(f"🚀 PHOENIX IS RUNNING!")
    print(f"🔗 Dashboard URL: {session.url}")
    print("="*50)
    print("\nLEAVE THIS WINDOW OPEN. Now open your app in another terminal.")
except Exception as e:
    print(f"❌ Failed to start Phoenix: {e}")
