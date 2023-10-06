from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import pandas as pd

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    download_orders_CSV_file()
    order_table = get_orders()
    order_robot(order_table)
    archive_receipts()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders_CSV_file():
    """Downloads Orders CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    library = Tables()
    orders = library.read_table_from_csv(path="orders.csv")
    return orders

def order_robot(orders):
    for order in orders:
        close_annoying_modal()
        fill_and_submit_order_form(order)
        #print(str(order["Order number"]))

def close_annoying_modal():
    page = browser.page()
    page.click("text='OK'")

def fill_and_submit_order_form(order):
    """Fills in the order data and click the 'Order' button to submit form"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click('//*[@id="id-body-'+str(order["Body"])+'"]')
    page.fill('//*[@placeholder="Enter the part number for the legs"]', str(order["Legs"]))
    page.fill("#address",str(order["Address"]))
    page.click("text='Order'")
    lst_elements = page.query_selector_all("#order-another")
    while lst_elements==[]:
        page.click("text='Order'")
        lst_elements = page.query_selector_all("#order-another")
    receipt_path = store_receipt_as_pdf(str(order["Order number"]))
    screenshot_path = screenshot_robot(str(order["Order number"]))
    embed_screenshot_to_receipt(screenshot_path, receipt_path)
    page.click("#order-another",timeout=3000)
    # while True:
    #     try:
    #         page.click("#order-another",timeout=3000)
    #         break
    #     except Exception as e:
    #         page.click("text='Order'")
    
def store_receipt_as_pdf(order_number):
    """Store receipt data to a pdf file"""
    receipt_path = "output/receipts/receipt_ordernumber"+order_number+".pdf"
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt,receipt_path)
    '''the first argument of pdf.html_to_pdf() contains html content as a string value. 
    Note that input must be well-formed and valid HTML. '''
    return receipt_path

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = "output/screenshots/receipt_ordernumber"+order_number+".png"
    page.screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot],target_document = pdf_file, append = True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip')