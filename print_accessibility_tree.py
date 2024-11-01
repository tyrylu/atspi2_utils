"""A script which either prints the entire accessibility tree as reachable from the first desktop or the subtree of the object which gains focus as the next a11y event received, maybe from a specific app. This script requires the pygobject and click python packages."""
import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
import time
import click
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def repr_object(object):
    return f"{object.get_role_name()} {object.get_name() or 'UNNAMED'}"

def print_object(object, level, max_depth, print_up_to_root=False):
    if print_up_to_root:
        up_to_root(object)
    def format_rel(rel):
        targets = [rel.get_target(i) for i in range(rel.get_n_targets())]
        return f"Relation of type {rel.relation_type.value_name} to {', '.join(repr_object(o) for o in targets)}"
    if max_depth is not None and level > max_depth:
        return
    print("*" * level + " " + repr_object(object))
    if state_descs := ', '.join(v.value_name for v in object.get_state_set().get_states()):
        print(f"States: {state_descs}")
    if relation_descs := ', '.join(format_rel(rel) for rel in object.get_relation_set()):
        print(f"Relations: {relation_descs}")
    if desc := object.get_description():
        print(f"Description: {desc}")
    if "Component" in object.get_interfaces():
        try:
            box = object.get_component_iface().get_extents(Atspi.CoordType.WINDOW)
            print(f"Object bounds: {box.width}x{box.height} rect at {box.x}, {box.y}")
        except NotImplementedError:
            pass
    if "Action" in object.get_interfaces():
        actions = object.get_action_iface()
        for action_idx in range(actions.get_n_actions()):
            try:
                print(f"Action {action_idx + 1}: {actions.get_name(action_idx)}, {actions.get_localizedName(action_idx) or 'no localized name'}, {actions.get_description(action_idx) or 'no description'}, {actions.get_keyBinding(action_idx) or 'no key bindings'}")
            except:
                pass
    for child_idx in range(object.get_child_count()):
        child = object.get_child_at_index(child_idx)
        print_object(child, level + 1, max_depth)

@click.command
@click.option("-f", "--focused", help="Print the tree for the next object which gains focus", is_flag=True)
@click.option("-l", "--list-apps", help="List the currently reachable applications", is_flag=True)
@click.option("-d", "--max-depth", help="Prints the tree to a given depth", default=None, type=int)
@click.option("-n", "--app-name", help="Prints the focused tree only if the event occurs in an app with the given name, or prints it tree", default=None)
@click.option("-c", "--num-focus-events", help="Print the given number of focus events", default=1, type=int)
def main(focused, list_apps, max_depth, app_name, num_focus_events):
    if focused:
        if app_name:
            print(f"Waiting for a focus event in {app_name}...")
        else:
                print("Waiting for a focus event...")
        num_events = 0
        def handler(evt):
            nonlocal num_events
            if app_name and evt.source.get_application().get_name() != app_name:
                return
            if not evt.detail1:
                return
            num_events += 1
            print_object(evt.source, 1, max_depth)
            if num_events == num_focus_events: Atspi.event_quit()
        listener = Atspi.EventListener.new(handler)
        listener.register("object:state-changed:focused")
        Atspi.event_main()
    elif list_apps:
        desktop = Atspi.get_desktop(0)
        for idx in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(idx)
            name = app.get_name()
            print(f"{idx + 1}: {name}")
    else:
        desktop = Atspi.get_desktop(0)
        root = None
        if not app_name:
            root = desktop
        else:
            root = None
            for idx in range(desktop.get_child_count()):
                app = desktop.get_child_at_index(idx)
                if app.get_name() == app_name:
                    root = app
                    break
            if root is None:
                print(f"Could not find application {app_name}")
                return

        print_object(root, 0, max_depth)

if __name__ == "__main__":
    main()
