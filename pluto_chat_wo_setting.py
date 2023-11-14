import threading
import time
from utils.my_radio import MyRadio
from transmission_module.operation_TX import operation_TX
from receiver_module.operation_RX import operation_RX
import queue

# SDR PARAMETERS

MHZ = int(1e6)
tx_lo_frequency = 1000 * MHZ
rx_lo_frequency = 900 * MHZ
sampling_rate = 10 * MHZ
bandwidth = 10 * MHZ
tx_gain = 0
rx_gain_type = 'slow_attack'
tx_sample_size = int(2**18)
rx_sample_size = int(2**16)


# Function to message transmission
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
    mySDR.tx_lo = tx_lo_frequency
    mySDR.rx_lo = rx_lo_frequency
    mySDR.sample_rate = sampling_rate
    mySDR.rx_rf_bandwidth = bandwidth
    mySDR.tx_rf_bandwidth = bandwidth
    mySDR.tx_hardwaregain_chan0 = tx_gain
    mySDR.gain_control_mode_chan0 = rx_gain_type
    mySDR.rx_buffer_size = rx_sample_size
    mySDR._tx_length = tx_sample_size

    return mySDR


# Function to show radio parameters
def show_radio_menu(mySDR):
    print("++++++ Radio Parameters ++++++")
    print(repr(mySDR))


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
        # print("3. Change Radio Parameters")
        print("3. Chat")
        print("4. Quit")
        choice = int(input())
        if choice == 1:
            mySDR = add_radio_menu()
        elif choice == 2:
            show_radio_menu(mySDR=mySDR)
        elif choice == 3:
            chat(mySDR)
        elif choice == 4:
            print("Quitting Program...")
            break


if __name__ == "__main__":
    mySDR = None
    print("Welcome to PlutoChat!")

    try:
        main_menu(mySDR=mySDR)
    except KeyboardInterrupt:
        print("\nApplication terminated by user. Goodbye!")
