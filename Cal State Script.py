#define variables and libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Keys, ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tempfile import NamedTemporaryFile
import csv
import time
import shutil

service = Service(executable_path="C:\\Users\\Trav\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
options = webdriver.ChromeOptions()
filename = 'C:\\Users\\Trav\\Downloads\\Fulfilmment Center Tracking.csv'
fields = ['Supplier ID', 'Supplier Name', 'Doing Buisiness As', 'Registration Status', 'Reg Sort', 'Location Count', 'Chico Location', 'Fresno Location', 'Bakersfield', 'FCs Added', 'Workflow']
tempfile = NamedTemporaryFile(mode='w', delete=False)
csubuy = webdriver.Chrome(service=service, options=options)
csubuy.implicitly_wait(10)
csubuy.get('https://solutions.sciquest.com/apps/Router/Login?OrgName=CalStateUniv&URL=')

#Generic search for save button
def save():
    saving = csubuy.find_elements(By.TAG_NAME, "input")
    for element in saving:
        if element.get_attribute("value") == "Save":
            csubuy.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            break

def smolsave():
    csubuy.switch_to.default_content()
    buframe = csubuy.find_element(By.XPATH, "//div[@id='ModalPopupIframeSave']")
    savebutton = buframe.find_element(By.XPATH, ".//input[@value='Save']")
    savebutton.click()

#Generic search for close button        
def close():
    close = csubuy.find_elements(By.CLASS_NAME, "ButtonReq")
    for element in close:
        if element.get_attribute("value") == "Close":
            csubuy.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            break
        
def smolclose():
        csubuy.switch_to.default_content()
        buframe = csubuy.find_element(By.XPATH, "//div[@id='ModalPopupIframeSave']")
        closebutton = buframe.find_element(By.XPATH, ".//input[@value='Close']")
        closebutton.click()

#Login to CSU BUY
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

#One time function to navigate to supplier directory
def prime():
    supplierbutton = csubuy.find_element(By.ID, "PHX_NAV_SupplierManagement_Img")
    ActionChains(csubuy).move_to_element(supplierbutton).perform()
    assert csubuy.find_element(By.ID, "PHX_NAV_SupplierManagement_Img").is_displayed()
    while not csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item").is_displayed():
        WebDriverWait(csubuy, 1).until(lambda csubuy: csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item"))
    suppliersearch = csubuy.find_element(By.ID, "PHX_NAV_TSMSearchForSupplier_Item").click()
    searchready = csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch")

#Search for Supplier, select the "Manage" button, and then navigate into the general details area
def search(supplierid, suppliername):
    leanname = suppliername.replace(" ", "")
    csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch")
    ActionChains(csubuy).send_keys(str(supplierid)).perform()
    assert csubuy.find_element(By.ID, "GSP_Suppliers_Search_Supplier_SimpleSearch").get_attribute('value') == supplierid
    searchbutton = csubuy.find_element(By.ID, "Button_Go").click()
    results = csubuy.find_element(By.XPATH, f"//a[starts-with(@id, '{leanname}')]")
    results.click()

def readiness_update():
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PHX_NAV_WORKFLOW_AND_REVIEW"))).click()
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_RegistrationWorkflow"))).click()
    WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "CMMSP_HeaderSupplierActions")))
    current_step = csubuy.find_element(By.CSS_SELECTOR, ".WfStepBox.CurrentWfStep")
    try:
        current_step.find_element(By.XPATH, ".//a[@aria-label='Hold']")
        return True
    except NoSuchElementException:
        returntosearch()
        return False
        
#Check if the About > General button is visible & selectable. If not, check if it's nested inside the "About" group. If not, return to search screen.
def classupdate():
    print("Attempting to access supplier classification field within general area.")
    try:
        general_link = csubuy.find_element(By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_CorporateInfo")
        print("Located General. Moving forward with updating classification.")
        general_link.click()
        supplier_type()
    except NoSuchElementException:
        print('unable to locate general link. Checking if it\'s nested inside the "About" group.')
        about = csubuy.find_element(By.ID, 'PHX_NAV_SupplierProfile')
        about.click()
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_CorporateInfo"))).click()
        print("Located About. Moving forward with updating classification.")
        supplier_type()
    except:
        print("Something is wrong")
        returntosearch()

#Function to update supplier classification to "Supplier"        
def supplier_type():  
        supplier_classification = csubuy.find_element(By.ID, "RegElement_18131_43")
        classification_value = Select(supplier_classification)
        classification_value.select_by_visible_text("Supplier")
        save()
        print("Supplier classification update complete.")

#Create fulfillment centers for Chico and Fresno
    #Logic statement:
    #If Chico = Yes and Fresno = Yes, create both (three) fulfillment centers
    #If Chico = Yes and Fresno = No, create Chico fulfillment center
    #If Chico = No and Fresno = Yes, create Fresno fulfillment centers (two)
    #If Chico = No and Fresno = No, do nothing
    #if fulfillment centers already exists, check if Chico/Freso are already marked primary. If so, do nothing.

def fcenter(chico, fresno):
    csubuy.find_element(By.ID, "PHX_NAV_ContactsAndLocations").click()
    csubuy.find_element(By.ID, "PhoenixNavLink_PHX_NAV_SupplierProfile_Fulfillment").click()
    if fresno == "Yes":
        buedit()
        csubuy.switch_to.default_content()
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        #Check if the fresno fulfillment center is already enabled. If not, enable it.
        frxno = csubuy.find_element(By.NAME, "FRXNO")
        if frxno.is_selected() == False:
            frxno.click()
        #Pause for the preferred checkbox to appear. if the fresno fulfillment center is already enabled as primary, ignore. If not, enable it as primary.
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.NAME, "FRXNO_IsPreferred")))
        frxpf = csubuy.find_element(By.NAME, "FRXNO_IsPreferred")
        if frxpf.is_selected() == False:
            frxpf.click()
        #Save & close dialogues and then move over to custom data section of fulfillment center
        smolsave()
        smolclose()
        csubuy.switch_to.default_content()
        customdata()
        fc_create()
        buedit()
        csubuy.switch_to.default_content()
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        frxth = csubuy.find_element(By.NAME, "FRXTH")
        if frxth.is_selected() == False:
            frxth.click()
        smolsave()
        smolclose()
        csubuy.switch_to.default_content()
        customdata()
    if chico == "Yes" and fresno == "Yes":
        fc_create()
        time.sleep(1)
    elif chico == "Yes" and fresno == "No":
        buedit()
        WebDriverWait(csubuy, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ModalPopupIframe")))
        assignments = csubuy.find_elements(By.TAG_NAME, 'input')
        for element in assignments:
            if element.get_attribute("name") == "CHXCO":
                csubuy.execute_script("arguments[0].scrollIntoView();", element)
                if element.is_selected() == False:
                    element.click()
                time.sleep(1)
                break
        WebDriverWait(csubuy, 3).until(EC.element_to_be_clickable((By.NAME, "CHXCO_IsPreferred")))
        chxpr = csubuy.find_element(By.NAME, "CHXCO_IsPreferred")
        if chxpr.is_selected() == False:
            chxpr.click()
        time.sleep(2)
        smolsave()
        smolclose()
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
    time.sleep(2)
    paygroup = csubuy.find_element(By.ID, "UDF_12841")
    paygroup_value = Select(paygroup)
    paygroup_value.select_by_visible_text("RE_Regular")
    handling = csubuy.find_element(By.ID, "UDF_12861")
    handling_value = Select(handling)
    handling_value.select_by_visible_text("RE_Regular")
    time.sleep(2)
    save()
    time.sleep(2)

#Create additional fulfillment center
def fc_create():
    newfc = csubuy.find_element(By.ID, "CmmSP_NewFulfillmentCenter").click()

#First, check supplier workflow status. If it is "Profile Complete", then proceed to workflow screen. If it is not "Profile Complete", then do nothing.
#If current workflow step = 3, then do nothing. If current workflow step = 2, then inspect supplier actions
#If "Approve/Complete Current Registration Workflow Step", do nothing and indicate in output. If "Approve/Complete Registration Workflow" is visible, then click and approve.
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
def returntosearch():
    csubuy.find_element(By.ID, "Back_To_Results_Search").click()
    csubuy.find_element(By.ID, "GSP_Suppliers_Search_NewSearch").click()

authy()
prime()
task_complete = "Yes"
updated_row = []
with open(filename, 'r') as csvfile, tempfile:
    supplierdata = csv.DictReader(csvfile, fieldnames=fields)
    writer = csv.DictWriter(tempfile, fieldnames=fields)
    for row in supplierdata:
        print("Beginning search for suppplier: " + row['Supplier Name'])
        if row['Registration Status'] == "Profile Complete" and row['FCs Added'] == "No":
            print("Supplier: " + row['Supplier Name'] + " is in scope and assessing information.")
            search(row['Supplier ID'], row['Supplier Name'])            
            if readiness_update() == True:
                print("Supplier: " + row['Supplier Name'] + " is still in hold status. Proceeding with instruction.")
                classupdate()
                print("Updated classification for :" + row['Supplier Name'])
                fcenter(row['Chico Location'], row['Fresno Location'])
                print("Created fulfillment centers for: " + row['Supplier Name'])
                row['Workflow'] = approve()
                print("Approved the registration workflow step for: " + row['Supplier Name'])
                newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "Yes", 'Workflow': row['Workflow']}
                writer.writerow(newrow)
                print("Updated CSV with progress for: " + row['Supplier Name'])
            else:
                print("Supplier: " + row['Supplier Name'] + " is not in hold status. Skipping to next supplier.")
                newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "No", 'Workflow': "Workflow Step Already Completed"}
                writer.writerow(newrow)
                print("Updated CSV with progress for: " + row['Supplier Name'])
        else:
            newrow = {'Supplier ID': row['Supplier ID'], 'Supplier Name': row['Supplier Name'], 'Doing Buisiness As': row['Doing Buisiness As'], 'Registration Status': row['Registration Status'], 'Reg Sort': row['Reg Sort'], 'Location Count': row['Location Count'], 'Chico Location': row['Chico Location'], 'Fresno Location': row['Fresno Location'],'Bakersfield': row['Bakersfield'], 'FCs Added': "No", 'Workflow': "Not Applicable"}
            writer.writerow(newrow)
            print("Supplier: " + row['Supplier Name'] + " is not in scope for this project.")

shutil.move(tempfile.name, filename)
csubuy.close()
csubuy.quit()