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
    if "Component in object.get_interfaces()":
        box = object.queryComponent().getExtents(pyatspi.WINDOW_COORDS)
        print(f"Object bounds: {box}")
    if "Action" in object.get_interfaces():
        actions = object.queryAction()
        for action_idx in range(actions.nActions):
            print(f"Action {action_idx + 1}: {actions.getName(action_idx)}, {actions.getLocalizedName(action_idx) or 'no localized name'}, {actions.getDescription(action_idx) or 'no description'}, {actions.getKeyBinding(action_idx) or 'no key bindings'}")
    for child in object:
        print_object(child, level + 1)

@click.command
@click.option("-f", "--focused", help="Print the tree for the next object which gains focus", is_flag=True)
@click.option("-a", "--nth-app", help="Prints the tree for the nth application", default=None, type=int)
@click.option("-l", "--list-apps", help="List the currently reachable applications", is_flag=True)
def main(focused, nth_app, list_apps):
    if focused:
        print("Waiting for a focus event...")
        def handler(evt):
            if not evt.detail1: return
            print_object(evt.source, 1)
            pyatspi.Registry.stop()
        pyatspi.Registry.registerEventListener(handler, "object:state-changed:focused")
        pyatspi.Registry.start()
    elif list_apps:
        for idx, app in enumerate(pyatspi.Registry.getDesktop(0)):
            print(f"{idx + 1}: {app.name}")
    elif nth_app is not None:
        print_object(pyatspi.Registry.getDesktop(0)[nth_app - 1], 0)
    else:
        print_object(pyatspi.Registry.getDesktop(0), 0)

if __name__ == "__main__":
    main()
