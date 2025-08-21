from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("http://localhost:5000")
implicitly_wait_timer = 500

driver.implicitly_wait(implicitly_wait_timer)

buttons = driver.find_elements(By.TAG_NAME, 'button')
signin_button = buttons[6]

signin_button.click()

driver.implicitly_wait(implicitly_wait_timer)

confirm_button = driver.find_elements(By.TAG_NAME, 'button')

driver.implicitly_wait(implicitly_wait_timer)

username = driver.find_element(By.ID, value="id")
password = driver.find_element(By.ID, value="passwd")
password_confirm = driver.find_element(By.ID, value="passwd_confirm")

driver.implicitly_wait(implicitly_wait_timer)

import random
username.send_keys('newuser' + str(random.randint(0, 100000)))
password.send_keys('1')
password_confirm.send_keys('1')

submit = driver.find_element(By.ID, 'submit')

submit.click()

driver.quit()