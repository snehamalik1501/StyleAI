from ollama import chat

response = chat(
    model='qwen2.5vl',
    messages=[
        {
            'role': 'user',
            'content': 'Suggest accessories for a black dress.'
        }
    ]
)

print(response['message']['content'])
