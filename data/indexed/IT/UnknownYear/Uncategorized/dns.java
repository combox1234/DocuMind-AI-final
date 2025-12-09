import java.net.*;
import java.util.Scanner;
 
public class DNSLookup {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in); // Scanner for user input
        int choice; // Variable to store user's menu choice
 
        // Loop to repeatedly display menu and process user choice
        do {
            // Displaying the menu options
            System.out.println("DNS Lookup Program");
            System.out.println("1. Domain to IP");
            System.out.println("2. IP to Domain");
            System.out.println("3. Exit");
 
            System.out.print("Enter choice: ");
            choice = sc.nextInt(); // Read user's choice
            sc.nextLine(); // Consume the leftover newline character
 
            try {
                // Option 1: Convert domain name to IP address
                if (choice == 1) {
                    System.out.print("Enter domain name (e.g. www.google.com): ");
                    String domain = sc.nextLine(); // Read domain input from user
                    InetAddress inet = InetAddress.getByName(domain); // Resolve domain to IP
                    System.out.println("IP Address: " + inet.getHostAddress()); // Display IP
                    System.out.println("------------------------------------------------------------------------------");
                }
                // Option 2: Convert IP address to domain name
                else if (choice == 2) {
                    System.out.print("Enter IP address (e.g. 8.8.8.8): ");
                    String ip = sc.nextLine(); // Read IP input from user
                    InetAddress inet = InetAddress.getByName(ip); // Resolve IP to domain
                    System.out.println("Domain Name: " + inet.getHostName()); // Display domain
                    System.out.println("------------------------------------------------------------------------------");
                }
                // Option 3: Exit the program
                else if (choice == 3) {
                    System.out.println("Exiting!!!");
                    return; // Exit the program
                }
                // Invalid choice entered
                else {
                    System.out.println("Invalid choice! Try Again!!!");
                    System.out.println("------------------------------------------------------------------------------");
                }
            } catch (UnknownHostException e) {
                // Handle case where lookup fails (invalid domain/IP)
                System.out.println("Lookup failed: " + e.getMessage());
            }
        } while(choice != 3); // Continue until user chooses to exit
 
        sc.close(); // Close the scanner to free resources
    }
}