from flask import Flask, request, jsonify
import re
import math
import os
import signal
import sys

app = Flask(__name__)

# Termux friendly graceful exit
if os.name != 'nt':  # Not Windows
    def signal_handler(sig, frame):
        print("\nStopping Flask app...")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

# Safe evaluation namespace (math functions + constants)
safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith('__')}
safe_dict.update({
    'abs': abs,
    'round': round,
    'max': max,
    'min': min
})

def preprocess_expression(expr):
    """Preprocess expression for safe evaluation"""
    # Remove spaces (optional, but we'll keep them for readability)
    expr = expr.strip()
    
    # Replace unicode superscripts with **digit
    superscript_map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
    }
    for sup, digit in superscript_map.items():
        expr = expr.replace(sup, f'**{digit}')
    
    # Replace ^ with **
    expr = expr.replace('^', '**')
    
    # Replace × and ÷
    expr = expr.replace('×', '*').replace('÷', '/')
    
    # Insert * for implicit multiplication
    # number followed by '('
    expr = re.sub(r'(\d)\s*\(', r'\1*(', expr)
    # ')' followed by number
    expr = re.sub(r'\)\s*(\d)', r')*\1', expr)
    # ')' followed by '('
    expr = re.sub(r'\)\s*\(', r')*(', expr)
    # number followed by letter (e.g., 2x) - but we don't have variables, so ignore
    # letter followed by number? not needed
    
    return expr

def safe_eval(expr):
    """Evaluate expression safely using restricted namespace"""
    try:
        # Preprocess
        processed = preprocess_expression(expr)
        # Evaluate with math functions
        result = eval(processed, {"__builtins__": {}}, safe_dict)
        return result, None
    except ZeroDivisionError:
        return None, "Division by zero"
    except SyntaxError:
        return None, "Invalid syntax"
    except NameError as e:
        return None, f"Unknown variable or function: {e}"
    except Exception as e:
        return None, str(e)

@app.route("/")
def home():
    return jsonify({
        "message": "Advanced Math API is running",
        "usage": "/math?expression=2(4+6)+sin(pi/2)"
    })

@app.route("/math", methods=["GET"])
def math_api():
    expression = request.args.get("expression")
    
    if not expression:
        return jsonify({
            "status": "error",
            "message": "Usage: /math?expression=2%2B3*5"
        }), 400
    
    result, error = safe_eval(expression)
    
    if error:
        return jsonify({
            "status": "error",
            "message": error,
            "expression": expression
        }), 400
    else:
        return jsonify({
            "status": "success",
            "expression": expression,
            "result": result
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)