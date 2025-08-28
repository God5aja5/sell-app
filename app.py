from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time, random, json, re, os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome! Use /<task_id> to run Selenium task."})

def run_selenium_task():
    # Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"

    # Use Service instead of executable_path
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://workik.com/ai-code-generator")
    time.sleep(6)
    actions = ActionChains(driver)

    # Step 1: Select model
    try:
        elem = driver.find_element(By.XPATH, "//span[contains(text(),'GPT 4.1 Mini')]")
        actions.move_to_element(elem).click().perform()
        time.sleep(2)
    except:
        pass

    # Step 2: Type random message
    random_texts = [
        "Make a simple calculator in Python",
        "Generate a todo list app in React",
        "Write HTML for a login form",
        "Give me CSS for a navbar"
    ]
    message = random.choice(random_texts)

    try:
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )
        driver.execute_script("""
            let box = arguments[0];
            let text = arguments[1];
            box.innerHTML = text;
            box.dispatchEvent(new InputEvent('input', { bubbles: true }));
        """, input_box, message)

        # Click send
        send_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiButtonBase-root.css-11uhnn1"))
        )
        send_btn.click()
        time.sleep(10)

        # Capture logs
        logs = driver.get_log("performance")
        curl_command = None
        tokens = {}

        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.requestWillBeSent":
                req = log["params"]["request"]
                url = req["url"]
                if "trigger?" in url and req["method"] == "POST":
                    headers = {k: v for k, v in req["headers"].items()}
                    post_data = req.get("postData", "")
                    curl_command = {
                        "url": url,
                        "method": "POST",
                        "headers": headers,
                        "data": post_data
                    }

                    # Extract tokens
                    try:
                        body = json.loads(post_data)
                        for key, val in body.items():
                            if isinstance(val, str):
                                if re.match(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$", val) or len(val) > 20:
                                    tokens[key] = val
                    except:
                        pass
                    break

        driver.quit()

        return {
            "message_sent": message,
            "curl": curl_command,
            "tokens": tokens
        }

    except Exception as e:
        driver.quit()
        return {"error": str(e)}

@app.route("/<task_id>", methods=["GET"])
def process(task_id):
    result = run_selenium_task()
    return jsonify({
        "task_id": task_id,
        "result": result
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
