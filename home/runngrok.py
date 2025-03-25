from pyngrok import ngrok

# Bắt đầu HTTP tunnel
http_tunnel = ngrok.connect(8000)
print(f"Public URL: {http_tunnel.public_url}")