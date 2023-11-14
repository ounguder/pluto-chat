import threading
import time
from utils.my_radio import MyRadio
from transmission_module.operation_TX import operation_TX
from receiver_module.operation_RX import operation_RX
import queue

MHZ = int(1e6)


# Function to transmit the message
def transmit_message(message, mySDR):
    msg = message
    operation_TX(mySDR, msg, False, False)


# Function to handle user input
def input_and_transmit(input_queue, exit_event, mySDR):
    while not exit_event.is_set():
        try:
            user_input = input_queue.get(timeout=1)
            if user_input is None:
                continue
            if user_input.lower() == 'q':
                exit_event.set(
                )  # Set the exit_event to signal both threads to exit
                break
            msg = user_input
            transmit_message(msg, mySDR)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except queue.Empty:  # Use the queue module for the exception
            pass


# Function to print a message every second
def print_message(exit_event, mySDR):
    while not exit_event.is_set():
        receivedMessage = operation_RX(mySDR, False)
        if receivedMessage == None:
            pass
        else:
            print(f'user: {receivedMessage}')
        time.sleep(1)


# Function to add a radio
def add_radio_menu():
    print("Adding a radio ")
    iIpAddress = input("Enter the ip address: ")
    iName = input("Enter your username:")
    mySDR = MyRadio(iIpAddress, iName)
    return mySDR


# Function to show radio parameters
def show_radio_menu(mySDR):
    print("++++++ Radio Parameters ++++++")
    print(repr(mySDR))


# Function to change radio parameters
def change_radio_menu(mySDR):
    while True:
        print("++++++++++ Parameter Selection +++++++++")
        print("1 - Tx Local Oscillator (MHz)")
        print("2 - Rx Local Oscillator (MHz)")
        print("3 - Sample Rate (MHz)")
        print("4 - Tx-Rx Bandwidth (MHz)")
        print("5 - Tx Gain (dB)")
        print("6 - Rx Gain Type and Gain (dB) ")
        print("7 - Tx Sample Size 2**N (Enter N)")
        print("8 - Rx Sample Size 2**N (Enter N)")
        print("9 - User Name")
        print("10 - Back")

        parameter_selection = int(input("Select a parameter to change: "))

        if parameter_selection == 1:
            value = int(input("Enter the Tx Frequency in MHz: "))
            mySDR.tx_lo = int(value * MHZ)
        elif parameter_selection == 2:
            value = int(input("Enter the Rx Frequency in MHz: "))
            mySDR.rx_lo = int(value * MHZ)
        elif parameter_selection == 3:
            value = int(input("Enter the Sample Rate in MHz: "))
            mySDR.sample_rate = int(value * MHZ)
        elif parameter_selection == 4:
            value = int(input("Enter the Bandwidth in MHz: "))
            mySDR.rx_rf_bandwidth = int(value * MHZ)
            mySDR.tx_rf_bandwidth = int(value * MHZ)
        elif parameter_selection == 5:
            value = int(input("Enter the Tx Gain in dB: "))
            mySDR.tx_hardwaregain_chan0 = value
        elif parameter_selection == 6:
            gainType = int(
                input(
                    "Enter the Rx Gain Type: \n 1-Manual\n2-Slow Attack \n3-Fast Attack: "
                ))
            if gainType == 1:
                value = int(input("Enter Rx Gain in dB: "))
                mySDR.gain_control_mode_chan0 = 'manual'
                mySDR.rx_hardwaregain_chan0 = value
            elif gainType == 2:
                mySDR.gain_control_mode_chan0 = 'slow_attack'
            elif gainType == 3:
                mySDR.gain_control_mode_chan0 = 'fast_attack'
        elif parameter_selection == 7:
            value = int(input("Enter the Tx Sample Size: "))
            mySDR._tx_length = int(2**value)
        elif parameter_selection == 8:
            value = int(input("Enter the Rx Sample Size: "))
            mySDR.rx_buffer_size = int(2**value)
        elif parameter_selection == 9:
            value = input("Enter the User Name: ")
            mySDR._user_name = value
        elif parameter_selection == 10:
            break


# Function to chat
def chat(mySDR):
    input_queue = queue.Queue()
    exit_event = threading.Event()

    transmission_thread = threading.Thread(target=input_and_transmit,
                                           args=(input_queue, exit_event,
                                                 mySDR))
    receiver_thread = threading.Thread(target=print_message,
                                       args=(exit_event, mySDR))

    transmission_thread.start()
    receiver_thread.start()

    try:
        while True:
            # user_input = input("Enter a message (or 'q' to quit): \n")
            user_input = input()
            input_queue.put(user_input)
            if user_input.lower() == 'q':
                break
    except KeyboardInterrupt:
        pass

    input_queue.put('q')

    transmission_thread.join()
    receiver_thread.join()


# Main menu
def main_menu(mySDR: MyRadio):
    while True:
        print("*** PlutoChat ***")
        print("1. Add a radio")
        print("2. Show the radio parameters")
        print("3. Change Radio Parameters")
        print("4. Chat")
        print("5. Quit")
        choice = int(input())
        if choice == 1:
            mySDR = add_radio_menu()
        elif choice == 2:
            show_radio_menu(mySDR=mySDR)
        elif choice == 3:
            change_radio_menu(mySDR=mySDR)
        elif choice == 4:
            chat(mySDR)
        elif choice == 5:
            print("Quitting Program...")
            break


if __name__ == "__main__":
    mySDR = None
    print("Welcome to PlutoChat!")

    try:
        main_menu(mySDR=mySDR)
    except KeyboardInterrupt:
        print("\nApplication terminated by user. Goodbye!")
