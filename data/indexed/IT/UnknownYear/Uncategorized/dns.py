import socket  

# Function to handle the DNS lookup operations
def dns_lookup():
    while True:
        # Display menu options
        print("DNS lookup program")
        print("1. domain to ip")
        print("2. ip to domain")
        print("3. exit")

        # Read user choice
        choice = input("enter choice: ")

        # Option 1: Convert domain name to IP address
        if choice == "1":
            domain = input("enter domain/website name (eg www.xyz.com): ")
            # Perform DNS lookup to get IP address from domain
            ip = socket.gethostbyname(domain)
            print("ip address received:", ip)
            print("------------------------------------------------------------------------------")

        # Option 2: Convert IP address to domain name
        elif choice == "2":
            ip = input("enter ip address (eg 8.8.8.8): ")
            # Perform reverse DNS lookup to get domain from IP
            domain = socket.gethostbyaddr(ip)[0]
            print("domain name:", domain)
            print("-------------------------------------------------------------------")
        # Option 3: Exit the program
        elif choice == "3":
            print("exiting........")
            break  # Exit the loop and terminate the program

        # Handle invalid menu choices
        else:
            print("invalid choice......try again")
            print("--------------------------------------------------------------------")

# Entry point of the program
if __name__ == "__main__":
    dns_lookup()
