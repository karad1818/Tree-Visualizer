from PyQt5.QtWidgets import QScrollArea ,QLabel ,QLineEdit , QApplication, QWidget , QDialog, QMainWindow ,QPushButton , QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QPainter, QBrush, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt
import sys
import math

class NaryNode:
    def __init__(self, value, parent=None):
        self.value = value
        self.children = []
        self.parent = parent
        self.x = 0
        self.y = 0
        self.level = 0
        self.subtree_pixel_width = 0 # For layout calculation

class Painting(QWidget):
    def __init__(self):
        super().__init__()
        self.root_node = None
        
        # Define drawing constants
        self.NODE_DIAMETER = 50
        self.SIBLING_SPACING = 30
        self.LEVEL_HEIGHT = 100 # Vertical spacing between levels
        self.NODE_TEXT_FONT = QFont('Arial', 10)
        # self.store and self.uniq_id are removed as they are no longer needed
        self.printHeight = 0

        self.add_input_box()

    def add_input_box(self):
        l = QLineEdit("",self)
        l.setGeometry(300, 35, 200, 20)
        label = QLabel("Enter Tree (e.g., A:B,C;B:D,E): ",self) 
        label.setGeometry(100, 35, 200, 13) 
        l.returnPressed.connect(lambda : take_data())
        self.heightLabel = QLabel("Height : N/A",self) # Keep a reference to update it
        self.heightLabel.setGeometry(100,50,170,13)
        
        def take_data():
            self.root_node = self._parse_input_to_nary_tree(l.text())
            if self.root_node:
                # Trigger recalculation of subtree widths and then repaint
                self._calculate_subtree_widths(self.root_node) 
                # Update widget size based on tree width (optional, but good for scrollbars)
                # This should ideally be done in WindowManipulation or by emitting a signal
                required_width = getattr(self.root_node, 'subtree_pixel_width', self.width()) + self.NODE_DIAMETER # Add some padding
                parent_scroll_area_widget = self.parentWidget()
                if parent_scroll_area_widget:
                     parent_scroll_area_widget.setMinimumWidth(max(self.width(), int(required_width)))

            self.repaint() 
            # Actual height calculation for N-ary tree can be done via a traversal if needed
            if self.root_node:
                self.printHeight = self._calculate_tree_height(self.root_node)
            else:
                self.printHeight = 0
            self.heightLabel.setText(f"Height : {self.printHeight}")

    def _calculate_tree_height(self, node):
        if node is None:
            return 0
        if not node.children:
            return 1  # Leaf node has height 1
        
        max_child_height = 0
        for child in node.children:
            max_child_height = max(max_child_height, self._calculate_tree_height(child))
        return 1 + max_child_height

    def _parse_input_to_nary_tree(self, input_str):
        # ... (previous parsing logic remains unchanged) ...
        if not input_str or input_str.isspace():
            return None

        nodes_map = {}
        
        declarations = input_str.split(';')
        if not declarations: 
            return None

        for decl_idx, decl_raw in enumerate(declarations):
            decl = decl_raw.strip()
            if not decl: 
                continue

            parts = decl.split(':', 1)
            parent_val = parts[0].strip()

            if not parent_val: 
                print(f"Warning: Empty parent value in declaration #{decl_idx+1} ('{decl_raw}'). Skipping.")
                continue

            if parent_val not in nodes_map:
                nodes_map[parent_val] = NaryNode(parent_val)
            parent_node = nodes_map[parent_val]

            if len(parts) > 1: 
                children_str = parts[1].strip()
                if children_str: 
                    child_values = children_str.split(',')
                    for child_idx, child_val_raw in enumerate(child_values):
                        child_val = child_val_raw.strip()
                        if not child_val: 
                            print(f"Warning: Empty child value in declaration for parent '{parent_val}' child #{child_idx+1}. Skipping.")
                            continue

                        if child_val not in nodes_map:
                            nodes_map[child_val] = NaryNode(child_val)
                        child_node = nodes_map[child_val]
                        
                        if child_node == parent_node:
                            print(f"Warning: Node '{child_val}' cannot be a child of itself. Skipping this relation for parent '{parent_val}'.")
                            continue
                        
                        if child_node.parent is not None and child_node.parent != parent_node:
                            print(f"Warning: Node '{child_val}' already has a parent '{child_node.parent.value}'. Cannot set new parent '{parent_val}'. Skipping this relation.")
                            continue
                        
                        if child_node not in parent_node.children: 
                           parent_node.children.append(child_node)
                        child_node.parent = parent_node 
        
        if not nodes_map: 
             return None
        
        root_candidates = [node for node in nodes_map.values() if node.parent is None]
        
        if len(root_candidates) == 1:
            return root_candidates[0]
        elif len(root_candidates) == 0:
            if nodes_map: 
                if len(nodes_map) == 1:
                    return list(nodes_map.values())[0]
                print("Warning: No root node found (all nodes have parents, possibly a cycle). Returning None.")
            return None 
        else: 
            print(f"Warning: Multiple root candidates found: {[r.value for r in root_candidates]}. Using the first one: '{root_candidates[0].value}'.")
            return root_candidates[0]

    def _draw_node_visual(self, painter, node_value, x, y, level):
        if level % 2 == 0:  # Even level
            brush_color = Qt.black
            pen_color = Qt.white
        else:  # Odd level
            brush_color = Qt.white
            pen_color = Qt.black
        
        painter.setBrush(QBrush(brush_color, Qt.SolidPattern))
        painter.setPen(QPen(pen_color, 1, Qt.SolidLine)) # Pen for ellipse and text
        
        painter.drawEllipse(int(x), int(y), self.NODE_DIAMETER, self.NODE_DIAMETER)
        
        painter.setFont(self.NODE_TEXT_FONT)
        
        st = str(node_value)
        if len(st) > 3:
            st = st[:2] + ".."  # Abbreviate long text
            
        fm = QFontMetrics(self.NODE_TEXT_FONT)
        text_width = fm.horizontalAdvance(st)
        # text_height = fm.height() # Not strictly needed for this centering but good to know
        ascent = fm.ascent()
        
        text_x = x + (self.NODE_DIAMETER - text_width) / 2
        ascent = fm.ascent()
        descent = fm.descent() # Calculate descent for precision
        # Using the more precise vertical centering formula from the subtask
        text_y = y + (self.NODE_DIAMETER + ascent) / 2 - (ascent - descent) / 2
        
        painter.drawText(int(text_x), int(text_y), st)

    def _calculate_subtree_widths(self, node):
        if not node:
            return 0
        
        if not node.children:
            node.subtree_pixel_width = self.NODE_DIAMETER
            return node.subtree_pixel_width
            
        total_children_subtree_width = 0
        for child in node.children:
            total_children_subtree_width += self._calculate_subtree_widths(child)
            
        node.subtree_pixel_width = total_children_subtree_width + max(0, len(node.children) - 1) * self.SIBLING_SPACING
        # Ensure a parent node is at least as wide as its own diameter if children are too narrow
        node.subtree_pixel_width = max(node.subtree_pixel_width, self.NODE_DIAMETER)
        return node.subtree_pixel_width

    def _draw_recursive(self, painter, node, current_x_center, current_y, level):
        if not node:
            return

        # Set Node Properties
        node.x = current_x_center - self.NODE_DIAMETER / 2
        node.y = current_y
        node.level = level

        # Draw Node
        self._draw_node_visual(painter, node.value, node.x, node.y, level)

        if not node.children:
            return

        # Children Drawing
        # Calculate the total width required by the children's subtrees plus spacing
        children_total_actual_width = sum(child.subtree_pixel_width for child in node.children)
        num_spacings = max(0, len(node.children) - 1)
        children_block_width = children_total_actual_width + num_spacings * self.SIBLING_SPACING
        
        start_x_for_children_area = current_x_center - children_block_width / 2
        child_y = current_y + self.LEVEL_HEIGHT
        current_child_x_start_point = start_x_for_children_area

        for child in node.children:
            child_center_x = current_child_x_start_point + child.subtree_pixel_width / 2
            
            # Draw Line
            parent_connector_x = node.x + self.NODE_DIAMETER / 2
            parent_connector_y = node.y + self.NODE_DIAMETER
            child_connector_x = child_center_x 
            child_connector_y = child_y # Connect to the top-center of the child node's bounding box

            line_pen = QPen(Qt.black, 1, Qt.SolidLine) # Separate pen for lines
            painter.setPen(line_pen)
            painter.drawLine(int(parent_connector_x), int(parent_connector_y), int(child_connector_x), int(child_connector_y))
            
            # Recursive Call
            self._draw_recursive(painter, child, child_center_x, child_y, level + 1)
            
            current_child_x_start_point += child.subtree_pixel_width + self.SIBLING_SPACING
            
    def paintEvent(self,event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Smoother lines and circles
        painter.setFont(self.NODE_TEXT_FONT) # Set default font early

        if self.root_node is None:
            # Clear previous drawings if any
            painter.fillRect(self.rect(), Qt.white) 
            painter.drawText(self.rect(), Qt.AlignCenter, "No tree to display or invalid input.")
            return

        # Clear previous drawings
        painter.fillRect(self.rect(), Qt.white)

        # Recalculate subtree widths every paintEvent if the tree structure could change dynamically
        # Or if window size changes affect layout. For simplicity, doing it here.
        # This assumes self.root_node is the actual root.
        if self.root_node:
             self._calculate_subtree_widths(self.root_node) # Calculate necessary widths

        # Determine initial drawing position
        # Use the actual width of the Painting widget for initial centering
        initial_x_center = self.width() / 2 
        
        # If the calculated width of the tree is wider than the widget, adjust the starting point
        # so the tree is drawn starting from a point that allows scrolling to see the whole tree.
        # The scroll area's widget (self) should have its minimumWidth set appropriately.
        if self.root_node and hasattr(self.root_node, 'subtree_pixel_width') and self.root_node.subtree_pixel_width > self.width():
            # Start drawing from the center of the tree's total width, ensuring some padding
            initial_x_center = self.root_node.subtree_pixel_width / 2 + 20 # As per subtask requirement
                                                                                            
        initial_y = 50 # As per subtask requirement
        
        self._draw_recursive(painter, self.root_node, initial_x_center, initial_y, 0)

class WindowManipulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,800,600) # Increased default window size
        self.setWindowTitle("N-ary Tree Visualizer")
        # self.setWindowIcon(QIcon('tree.jpg')) 
        self.setWindowOpacity(1)

        # This is the widget that will be scrolled.
        # The Painting widget itself will be placed on this scroll_content_widget.
        self.scroll_content_widget = QWidget()
        
        layout = QVBoxLayout(self.scroll_content_widget) # Layout for the scroll_content_widget
        self.painting_widget = Painting() 
        layout.addWidget(self.painting_widget)
        self.scroll_content_widget.setLayout(layout)

        # Set initial size for the scrollable content.
        # This should be large enough for typical trees or be dynamically adjusted.
        self.scroll_content_widget.setMinimumSize(2000, 1500) # Default size for scrollable area
        # The Painting widget will resize with its parent layout if not fixed size.

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Important: Allows the inner widget (scroll_content_widget) to resize
        self.scroll_area.setWidget(self.scroll_content_widget)
        
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Main layout for the WindowManipulation widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowManipulation()
    window.show()
    sys.exit(app.exec_())
