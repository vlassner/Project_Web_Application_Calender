from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("http://localhost:5000")
implicitly_wait_timer = 500

driver.implicitly_wait(implicitly_wait_timer)

buttons = driver.find_elements(By.TAG_NAME, 'button')
login_button = buttons[5]

login_button.click()

driver.implicitly_wait(implicitly_wait_timer)

confirm_button = driver.find_elements(By.TAG_NAME, 'button')

driver.implicitly_wait(implicitly_wait_timer)

username = driver.find_element(By.ID, value="id")
password = driver.find_element(By.ID, value="passwd")

driver.implicitly_wait(implicitly_wait_timer)

username.send_keys('tmota')
password.send_keys('1')

submit = driver.find_element(By.ID, 'submit')

submit.click()

driver.implicitly_wait(implicitly_wait_timer)

buttons = driver.find_elements(By.TAG_NAME, 'button')
create_offer_button = buttons[4]

create_offer_button.click()

driver.implicitly_wait(implicitly_wait_timer)

date = driver.find_element(By.ID, 'date')
event_or_task = driver.find_element(By.ID, 'event_or_task')

date.send_keys('5\t12\t2024\t10\t22\ta')
event_or_task.send_keys('t')

submit = driver.find_element(By.ID, 'submit')
submit.click() # creates offer under tmota's name

date = driver.find_element(By.ID, 'date')
event_or_task = driver.find_element(By.ID, 'event_or_task')

date.send_keys('5\t12\t2024\t10\t22\ta')
event_or_task.send_keys('a')

submit = driver.find_element(By.ID, 'submit')
submit.click() # creates offer under tmota's name

driver.implicitly_wait(implicitly_wait_timer)

buttons = driver.find_elements(By.ID, 'signout')

signout_button = buttons[0]
signout_button.click() # signs out after creating offer

driver.quit()