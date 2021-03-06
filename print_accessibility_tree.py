"""A script which either prints the entire accessibility tree as reachable from the first desktop or the subtree of the object which gains focus as the next a11y event received. This script requires the pyatspi and click python packages."""
import pyatspi
import click

def print_object(object, level):
    def format_rel(rel):
        targets = [rel.get_target(i) for i in range(rel.get_n_targets())]
        return f"Relation of type {rel.relation_type.value_name} to {', '.join(str(o) for o in targets)}"
    print("*" * level + " " + str(object))
    if state_descs := ', '.join(v.value_name for v in object.get_state_set().get_states()):
        print(f"States: {state_descs}")
    if relation_descs := ', '.join(format_rel(rel) for rel in object.get_relation_set()):
        print(f"Relations: {relation_descs}")
    if desc := object.get_description():
        print(f"Description: {desc}")
    for child in object:
        print_object(child, level + 1)

@click.command
@click.option("-f", "--focused", help="Print the tree for the next object which gains focus", is_flag=True)
def main(focused):
    if focused:
        print("Waiting for a focus event...")
        def handler(evt):
            print_object(evt.source, 1)
            pyatspi.Registry.stop()
        pyatspi.Registry.registerEventListener(handler, "object:state-changed:focused")
        pyatspi.Registry.start()
    else:
        print_object(pyatspi.Registry.getDesktop(0), 0)

if __name__ == "__main__":
    main()