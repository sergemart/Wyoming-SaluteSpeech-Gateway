__package__ = 'wyoming_salutespeech_gateway'

# noinspection PyUnresolvedReferences
from . import app
# noinspection PyUnresolvedReferences
from . import client


app.parse_arguments()
app.setup_custom_logger("root")

test_data = [
    {
        "input": "<think> content_to_drop </think>payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "payload_to_keep<think> content_to_drop </think>",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> content_to_drop <tag1>content_to_drop</tag1>  </think>payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> content_to_drop <tag1>content_to_drop<tag2>content_to_drop</tag2></tag1>  </think>payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> content_to_drop <tag1>content_to_drop<tag2>content_to_drop</tag2></tag1>  </think>payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> content_to_drop <tag1>content_to_drop</tag1></think>payload_to_keep<tag2>content_to_drop</tag2>",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "  <think> content_to_drop </think> payload_to_keep ",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think> content_to_drop\ncontent_to_drop\ncontent_to_drop </think> payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think>payload_to_keep",
        "expected": "payload_to_keep"
    },
    {
        "input": "<think>content_to_drop</think>",
        "expected": ""
    },
    {
        "input": "<think>",
        "expected": ""
    },
    {
        "input": "",
        "expected": ""
    }
]

for case in test_data:
    text = case['input']
    expected = case['expected']
    result = app.get_synthesize_payload( text )
    if result == expected:
        print("PASS")
    else:
        print(f"FAIL:")
        print(f"\tinput:\t\t {text}")
        print(f"\tresult:\t\t {result}")
        print(f"\texpected:\t {expected}")
