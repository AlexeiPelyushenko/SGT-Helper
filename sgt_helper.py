# TODO make selecting topics more convenient. It's inconvenient to have to type out the whole topic name. Maybe do by number or "autocomplete"
# TODO search: eventually there'll be a lot of topics, probably. Could be convenient to search either by topic or by keywords in content.
# TODO GUI: might use pygame/pygame_gui cause I like it. But a GUI of some sort would be nice.

import json, os, time

def main():
    json_path = "info.json"
    
    if not os.path.exists(json_path):
        with open(json_path, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(json_path, "r", encoding="utf-8") as f:
        data_store = json.load(f)
        
    done = False
    quit_with_saving = True
    try:
        while not done:
            os.system("cls")
            print("Welcome to the Spectral Graph Theory Helper program. Select a topic below and you can either read about the topic/what is stored, or write new information into that topic.")
            print("-----------------------------")
            count = 1
            for item in data_store.keys():
                print(f"{count}: {item}")
                count += 1
            print()
            print(f"Add a new topic (add)")
            print(f"Delete a topic (delete)")
            print(f"Quit (quit)")
            print(f"Quit without saving (nosave)")
            inp = input("\nSelect a topic to work with or action to perform: ")
            
            if inp == "add":
                addition = input("What topic would you like to add?: ")
                data_store[addition] = []
            elif inp == "delete":
                delete = input("Which topic?: ")
                del data_store[delete]
            elif inp == "quit":
                done = True
            elif inp == "nosave":
                done = True
                quit_with_saving = False
            elif inp in data_store.keys():
                action = input("Read information about the topic, add or delete information? (read/add/delete): ")
                if action == "read":
                    os.system("cls")
                    print("Info:\n")
                    count = 1
                    for item in data_store[inp]:
                        print(f"{count}: {item}\n")
                        count += 1
                    print("---------------------")
                    input("Press enter to return to the home page...")
                elif action == "add":
                    done_adding = False
                    while not done_adding:
                        addition = input(f"Type out what you'd like to add to the entry '{inp}' or type done to finish:\n")
                        if addition == "done":
                            done_adding = True
                        else:
                            data_store[inp].append(addition)
                elif action == "delete":
                    done_deleting = False
                    while not done_deleting:
                        os.system("cls")
                        print("Info:\n")
                        count = 1
                        for item in data_store[inp]:
                            print(f"{count}: {item}\n")
                            count += 1
                        print("---------------------")
                        index = input("Type in the number item you'd like to delete or done to finish: ")
                        if index == "done":
                            done_deleting = True
                        else:
                            index = int(index) - 1
                            if 0 <= index and index < len(data_store[inp]):
                                del data_store[inp][int(index) - 1]
                            else:
                                print("Bad index.")
                                time.sleep(0.75)
            else:
                print("Invalid topic.")
                time.sleep(1)
                os.system("cls")
    finally:
        print("yaba daba doo")
        if quit_with_saving:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data_store, f, indent=4)
    
    
if __name__ == "__main__":
    main()