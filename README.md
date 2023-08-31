# suppliercorrections

class_update()

Inside the function, it first tries to find an element with the ID "PhoenixNavLink_PHX_NAV_SupplierProfile_CorporateInfo" using the find_element method the csubuy object (which seems to be a web driver). If the element is found, it prints a message, clicks on the element, and then calls a function named supplier_type.

If the element is not found, it catches a NoSuchElementException and prints a message indicating that it will check if the element is nested inside the "About" group. It finds the "About" element using another ID and clicks on it. Then it waits for 3 seconds for the element to be clickable and clicks on it. After that, it prints a message and calls the supplier_type function.

If any other exception occurs, it catches it and prints a message indicating that something is wrong. Then it calls a returntosearch function.

Please note that the code snippet mentions some external objects and functions (csubuy, By.ID, NoSuchElementException, etc.) that are not defined in the provided code.
