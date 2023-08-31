#define variables and libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Keys, ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tempfile import NamedTemporaryFile
import csv
import time
import shutil

service = Service(executable_path="C:\\Users\\Trav\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
options = webdriver.ChromeOptions()
filename = 'C:\\Users\\Trav\\Downloads\\Fulfilmment Center Tracking.csv'
fields = ['Supplier ID', 'Supplier Name', 'Doing Buisiness As', 'Registration Status', 'OFAC SDN Status', 'Reg Sort', 'Location Count', 'Chico Location', 'Fresno Location', 'Bakersfield', 'FCs Added']
tempfile = NamedTemporaryFile(mode='w', delete=False)
csubuy = webdriver.Chrome(service=service, options=options)
csubuy.implicitly_wait(1)
csubuy.get('https://solutions.sciquest.com/apps/Router/Login?OrgName=CalStateUniv&URL=')

# Function to look for the save button & select it. This is used for the general save button and the small save button within frames.
def save(type):
    if type == "generic":
        saving = csubuy.find_elements(By.TAG_NAME, "input")
        for element in saving:
            if element.get_attribute("value") == "Save":
                csubuy.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                break
            return
    elif type == "small":
        csubuy.switch_to.default_content()
        buframe = csubuy.find_element(By.XPATH, "//div[@id='ModalPopupIframeSave']")
        savebutton = buframe.find_element(By.XPATH, ".//input[@value='Save']")
        savebutton.click()
        return

# Function to look for the close button & select it. This is used for the general close button and close buttons within frames.      
def close(type):
    if type == "generic":
        close = csubuy.find_elements(By.CLASS_NAME, "ButtonReq")
        for element in close:
            if element.get_attribute("value") == "Close":
                csubuy.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                break
            return
    elif type == "small":
        csubuy.switch_to.default_content()
        buframe = csubuy.find_element(By.XPATH, "//div[@id='ModalPopupIframeSave']")
        closebutton = buframe.find_element(By.XPATH, ".//input[@value='Close']")
        closebutton.click()
        return

# Login to CSU BUY
def authy():
    #Username input
    username = csubuy.find_element(By.ID, "Username")
    ActionChains(csubuy).send_keys_to_element(username, "Tvasceannie").perform()
    assert csubuy.find_element(By.ID, "Username").get_attribute('value') == "Tvasceannie"
    
    #Password input
    password = csubuy.find_element(By.ID, "Password")
    ActionChains(csubuy).send_keys_to_element(password, "RiseNow123").perform()
    assert csubuy.find_element(By.ID, "Password").get_attribute('value') == "RiseNow123"
    
    #Interact with login button
    login = csubuy.find_element(By.XPATH, "//button[@type='submit']")
    login.click()
    
    # Move to the supplier directory after logging in.
    supplierbutton = csubuy.find_element(By.ID, "PHX_NAV_SupplierManagement_Img")
    ActionChains(csubuy).move_to_element(supplierbutton).perform()
    assert csubuy.find_element(By.ID, "PHX_NAV_SupplierManagement_Img").is_displayed()
    while not csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item").is_displayed():
        WebDriverWait(csubuy, 1).until(lambda csubuy: csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item"))
    csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item").click()
    csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch")

# Search for Supplier, select the "Manage" button, and then navigate into the general details area
def search(supplierid, suppliername):
    leanname = suppliername.replace(" ", "")
    csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch")
    ActionChains(csubuy).send_keys(str(supplierid)).perform()
    assert csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch").get_attribute('value') == supplierid
    csubuy.find_element(By.ID, "Button_Go").click()
    time.sleep(1)
    query = csubuy.find_element(By.CLASS_NAME, "SearchResults")
    results = query.find_elements(By.XPATH, "//a[contains(@id, '_Link')]")
    for link in results:
        if 'SupplierID=' in link.get_attribute("href"):
            link.click()
            break
    return

# preliminary check to see if the supplier is still in holding status.
def check_status():
    print("Attempting to access supplier workflow page")
    WebDriverWait(csubuy, 2).until(EC.element_to_be_clickable((By.ID, "PHX_NAV_WORKFLOW_AND_REVIEW"))).click()
    WebDriverWait(csubuy, 2).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_RegistrationWorkflow"))).click()
    try:
        print("Checking to see if the supplier current workflow step is in holding status.")
        time.sleep(1)
        current_step = csubuy.find_element(By.CLASS_NAME, "CurrentWfStep")
        wf_step = current_step.find_element(By.CLASS_NAME, "WfStepName").text
        if wf_step == "Hold":
            print("Supplier is still in holding status. We will proceed.")
            return True
    except NoSuchElementException:
        print("I couldn't find a current workflow step. Let's make sure the supplier status isn't approved or the workflow is already complete.")
        approval_state = csubuy.find_element(By.XPATH, '//*[@id="SupplierRegistrationApprovals_body"]/div[6]/div[2]/div/div/div[1]/form/div/div[2]/div/div[2]/div[2]/div')
        if approval_state.text == "Approved":
            print("Supplier is already approved. Let's move on.")
            return False
    except:
        print("Something is wrong. Unable to access supplier workflow page. Let's move on")
        return False
                
#Check if the About > General button is visible & selectable. If not, check if it's nested inside the "About" group. If not, return to search screen.
def class_update():
    print("Now beginning attempts to access supplier classification field within general area.")
    try:
        general_link = csubuy.find_element(By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_CorporateInfo")
        print("Located General. Moving forward with updating classification.")
        general_link.click()
        supplier_type()
    except NoSuchElementException:
        print('Unable to locate general link. Checking if it is nested inside the "About" group.')
        about = csubuy.find_element(By.ID, 'PHX_NAV_SupplierProfile')
        about.click()
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_CorporateInfo"))).click()
        print("Located About. Moving forward with updating classification.")
        supplier_type()
    except:
        print("Something is wrong. Let's move on.")
        returntosearch()

#Function to update supplier classification to "Supplier"        
def supplier_type():  
        supplier_classification = csubuy.find_element(By.ID, "RegElement_18131_43")
        classification_value = Select(supplier_classification)
        classification_value.select_by_visible_text("Supplier")
        save("generic")
        print("Supplier classification update complete.")

# Create fulfillment centers for Chico and Fresno
def fcenter(chico, fresno):
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PHX_NAV_ContactsAndLocations"))).click()
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_Fulfillment"))).click()
    if fresno == "Yes": # begin logic to update and create fulfillment center for fresno & fresno athletics
        buedit()
        csubuy.switch_to.default_content()
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        
        frxno = csubuy.find_element(By.NAME, "FRXNO") #Check if the fresno fulfillment center is already enabled. If not, enable it.
        if frxno.is_selected() == False:
            frxno.click()
        
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.NAME, "FRXNO_IsPreferred"))) #Pause for the preferred checkbox to appear. if the fresno fulfillment center is already enabled as primary, ignore. If not, enable it as primary.
        frxpf = csubuy.find_element(By.NAME, "FRXNO_IsPreferred")
        if frxpf.is_selected() == False:
            frxpf.click()
            
        save("small")
        close("small")
        csubuy.switch_to.default_content()
        customdata()
        fc_create() # Create a new FC
        buedit()
        csubuy.switch_to.default_content()
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        frxth = csubuy.find_element(By.NAME, "FRXTH")
        if frxth.is_selected() == False:
            frxth.click()
        save("small")
        close("small")
        csubuy.switch_to.default_content()
        customdata()
    if chico == "Yes" and fresno == "Yes": # If both chico and fresno are enabled, then create a new FC for chico
        fc_create()
    elif chico == "Yes" and fresno == "No": # If only chico is enabled, then create a new FC for chico. This is primarily done this way to ignore the scenario of only fresno being enabled.
        buedit()
        
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        assignments = csubuy.find_elements(By.TAG_NAME, 'input')
        for element in assignments:
            if element.get_attribute("name") == "CHXCO":
                csubuy.execute_script("arguments[0].scrollIntoView();", element)
                if element.is_selected() == False:
                    element.click()
                break
            
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.NAME, "CHXCO_IsPreferred"))) # Pause for the preferred checkbox to appear. If the chico fulfillment center is already enabled as primary, ignore. If not, enable it as primary.
        chxpr = csubuy.find_element(By.NAME, "CHXCO_IsPreferred")
        if chxpr.is_selected() == False:
            chxpr.click()
        
        save("small")
        close("small")
        csubuy.switch_to.default_content()
        customdata()

#Open up frame to edit BU assignments
def buedit():
    bus = csubuy.find_elements(By.TAG_NAME, "a")
    for felement in bus:
        if felement.text == ">>Edit Assignments":
            csubuy.execute_script("arguments[0].scrollIntoView();", felement)
            felement.click()
            break
        
#Open custom data and update pay group and handling        
def customdata():
    custominfo = csubuy.find_elements(By.CLASS_NAME, "TabLinkLevel1")
    for element in custominfo:
        if element.text == "Custom Data":
            csubuy.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            break
    paygroup = csubuy.find_element(By.ID, "UDF_12841")
    paygroup_value = Select(paygroup)
    paygroup_value.select_by_visible_text("RE_Regular")
    handling = csubuy.find_element(By.ID, "UDF_12861")
    handling_value = Select(handling)
    handling_value.select_by_visible_text("RE_Regular")
    save("generic")

#Create additional fulfillment center
def fc_create():
    csubuy.find_element(By.ID, "CmmSP_NewFulfillmentCenter").click()

#Approve workflow step
def approve():
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PHX_NAV_WORKFLOW_AND_REVIEW"))).click()
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_RegistrationWorkflow"))).click()
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "CMMSP_HeaderSupplierActions")))
    current_step = csubuy.find_element(By.CSS_SELECTOR, ".WfStepBox.CurrentWfStep")
    try:
        current_step.find_element(By.XPATH, ".//a[@aria-label='Hold']")
        csubuy.find_element(By.ID, "CMMSP_HeaderSupplierActions").click()
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "ApproveCompleteRegistrationWorkflowStep"))).click()
        time.sleep(2)
        returntosearch()
    except NoSuchElementException:
        returntosearch()
        return "Workflow Step Already Completed"
    return "Workflow Step Completed"
    
#Return to search screen
#Return to search screen
def returntosearch():
    try:
        links = csubuy.find_elements(By.CLASS_NAME, "linkText")
        for link in links:
            if link.text == "Back to Results":
                link.click()
                break
        WebDriverWait(csubuy, 1).until(EC.element_to_be_clickable((By.ID, "GSP_Suppliers_Search_NewSearch"))).click()
        return
    except NoSuchElementException:
        print("The return to search button isn't where it should be, going through the breadcrumb.")
        csubuy.find_element(By.ID, "Phoenix_BreadCrumb_PHX_NAV_TSMSearchForSupplier_Invoker").click()
        WebDriverWait(csubuy, 1).until(EC.element_to_be_clickable((By.ID, "bc_PHX_NAV_TSMSearchForSupplier_Item"))).click()
        time.sleep(1)
        return

authy()
with open(filename, 'r') as csvfile, open("temp.csv", 'w') as tempfile:
    supplierdata = csv.DictReader(csvfile, fieldnames=fields)
    writer = csv.DictWriter(tempfile, fieldnames=fields)
    for row in supplierdata:
        if row['Registration Status'] == "Profile Complete" and row['OFAC SDN Status'] == "Check Not Run" and row['FCs Added'] == "No":
            print("Supplier: " + row['Supplier Name'] + " is in scope and assessing information.")
            search(row['Supplier ID'], row['Supplier Name'])            
            if check_status() == True:
                class_update()
                print("Updated classification for :" + row['Supplier Name'])
                fcenter(row['Chico Location'], row['Fresno Location'])
                print("Created fulfillment centers for: " + row['Supplier Name'])
                row['Workflow'] = approve()
                print("Approved the registration workflow step for: " + row['Supplier Name'])
                newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'OFAC SDN Status': row['OFAC SDN Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "Yes"}
                writer.writerow(newrow)
                print("Updated CSV with progress for: " + row['Supplier Name'])

            else:
                returntosearch()
                newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'OFAC SDN Status': row['OFAC SDN Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "No"}
                writer.writerow(newrow)
                print("Supplier: " + row['Supplier Name'] + " is not in scope for this project.")
        
        else:
            newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'OFAC SDN Status': row['OFAC SDN Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "No"}
            writer.writerow(newrow)
            print("Supplier: " + row['Supplier Name'] + " is not in scope for this project.")
    
# Save the final csv before finishing
tempfile.flush()
time.sleep(2)
tempfile.close()
shutil.move(tempfile.name, filename)

csubuy.close()
csubuy.quit()