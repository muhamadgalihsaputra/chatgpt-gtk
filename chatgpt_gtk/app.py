import os
import sys
import json
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
gi.require_version('GLib', '2.0')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, WebKit, GLib, Gdk, Gio

APP_ID = "io.github.chatgpt_gtk.desktop"
DEFAULT_URL = "https://chatgpt.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/133.0.0.0 Safari/537.36"
)

DATA_DIR = os.path.expanduser("~/.local/share/chatgpt-gtk")
CACHE_DIR = os.path.expanduser("~/.cache/chatgpt-gtk")
CONFIG_DIR = os.path.expanduser("~/.config/chatgpt-gtk")
CONFIG_FILE = os.path.join(CONFIG_DIR, "window_state.json")


def load_window_state():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"width": 1080, "height": 800, "is_maximized": False}


def save_window_state(width, height, is_maximized):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"width": width, "height": height, "is_maximized": is_maximized}, f)
    except Exception:
        pass


class ChatGPTWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="ChatGPT")
        self.app = app
        
        # Window sizing & state
        state = load_window_state()
        self.set_default_size(state.get("width", 1080), state.get("height", 800))
        if state.get("is_maximized", False):
            self.maximize()

        self.connect("close-request", self.on_close_request)

        # Persistent Network Session
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.session = WebKit.NetworkSession.new(
            data_directory=DATA_DIR,
            cache_directory=CACHE_DIR
        )

        # WebKit Settings
        self.settings = WebKit.Settings()
        self.settings.set_user_agent(USER_AGENT)
        self.settings.set_enable_developer_extras(True)
        self.settings.set_enable_webrtc(True)
        self.settings.set_enable_media_stream(True)
        self.settings.set_javascript_can_access_clipboard(True)
        self.settings.set_hardware_acceleration_policy(
            WebKit.HardwareAccelerationPolicy.ON_DEMAND
        )

        # Main Layout Box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # HeaderBar (Inherits GNOME theme & left button-layout)
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class("flat")
        self.main_box.append(self.header_bar)

        # Window Title Widget
        self.title_widget = Adw.WindowTitle(title="ChatGPT", subtitle="chatgpt.com")
        self.header_bar.set_title_widget(self.title_widget)

        # Navigation Controls (Left side of header, right after traffic lights)
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.header_bar.pack_start(self.nav_box)

        self.btn_back = Gtk.Button(icon_name="go-previous-symbolic")
        self.btn_back.set_tooltip_text("Kembali (Alt+Left)")
        self.btn_back.connect("clicked", self.on_back_clicked)
        self.btn_back.set_sensitive(False)
        self.nav_box.append(self.btn_back)

        self.btn_forward = Gtk.Button(icon_name="go-next-symbolic")
        self.btn_forward.set_tooltip_text("Maju (Alt+Right)")
        self.btn_forward.connect("clicked", self.on_forward_clicked)
        self.btn_forward.set_sensitive(False)
        self.nav_box.append(self.btn_forward)

        self.btn_reload = Gtk.Button(icon_name="view-refresh-symbolic")
        self.btn_reload.set_tooltip_text("Muat Ulang (Ctrl+R)")
        self.btn_reload.connect("clicked", self.on_reload_clicked)
        self.nav_box.append(self.btn_reload)

        self.btn_home = Gtk.Button(icon_name="go-home-symbolic")
        self.btn_home.set_tooltip_text("Beranda ChatGPT")
        self.btn_home.connect("clicked", lambda _: self.web_view.load_uri(DEFAULT_URL))
        self.nav_box.append(self.btn_home)

        # Right side actions (Menu button)
        self.menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        self.menu_btn.set_tooltip_text("Menu Aplikasi")
        self.header_bar.pack_end(self.menu_btn)
        self.setup_menu()

        # Progress bar at the top of content
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.add_css_class("osd")
        self.progress_bar.set_visible(False)
        self.main_box.append(self.progress_bar)

        # Primary WebView
        self.web_view = WebKit.WebView(network_session=self.session)
        self.web_view.set_settings(self.settings)
        self.web_view.set_vexpand(True)
        self.web_view.set_hexpand(True)
        self.main_box.append(self.web_view)

        # Connect WebView Signals
        self.web_view.connect("notify::estimated-load-progress", self.on_progress_changed)
        self.web_view.connect("notify::title", self.on_title_changed)
        self.web_view.connect("notify::uri", self.on_uri_changed)
        self.web_view.connect("load-changed", self.on_load_changed)
        self.web_view.connect("create", self.on_create_popup)
        self.web_view.connect("permission-request", self.on_permission_request)

        # Key controller for shortcuts
        self.setup_shortcuts()

        # Initial Load
        self.web_view.load_uri(DEFAULT_URL)

    def setup_menu(self):
        menu = Gio.Menu()
        
        # View Section
        view_section = Gio.Menu()
        view_section.append("Perbesar (Ctrl++)", "app.zoom_in")
        view_section.append("Perkecil (Ctrl+-)", "app.zoom_out")
        view_section.append("Reset Zoom (Ctrl+0)", "app.zoom_reset")
        menu.append_section(None, view_section)

        # Tools Section
        tools_section = Gio.Menu()
        tools_section.append("Salin URL Halaman", "app.copy_url")
        tools_section.append("Buka Web Inspector (F12)", "app.inspect")
        tools_section.append("Hapus Cache", "app.clear_cache")
        menu.append_section(None, tools_section)

        # App Section
        app_section = Gio.Menu()
        app_section.append("Tentang ChatGPT GTK", "app.about")
        app_section.append("Keluar (Ctrl+Q)", "app.quit")
        menu.append_section(None, app_section)

        self.menu_btn.set_menu_model(menu)

    def setup_shortcuts(self):
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(controller)

    def on_key_pressed(self, controller, keyval, keycode, state):
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK) != 0
        alt = (state & Gdk.ModifierType.ALT_MASK) != 0

        if ctrl:
            if keyval in (Gdk.KEY_r, Gdk.KEY_R):
                self.web_view.reload()
                return True
            elif keyval in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
                self.zoom_in()
                return True
            elif keyval in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
                self.zoom_out()
                return True
            elif keyval in (Gdk.KEY_0, Gdk.KEY_KP_0):
                self.zoom_reset()
                return True
            elif keyval in (Gdk.KEY_q, Gdk.KEY_Q):
                self.app.quit()
                return True
        elif alt:
            if keyval == Gdk.KEY_Left:
                if self.web_view.can_go_back():
                    self.web_view.go_back()
                return True
            elif keyval == Gdk.KEY_Right:
                if self.web_view.can_go_forward():
                    self.web_view.go_forward()
                return True
        elif keyval == Gdk.KEY_F11:
            if self.is_fullscreen():
                self.unfullscreen()
            else:
                self.fullscreen()
            return True
        elif keyval == Gdk.KEY_F12:
            inspector = self.web_view.get_inspector()
            if inspector.is_attached():
                inspector.close()
            else:
                inspector.show()
            return True

        return False

    def zoom_in(self):
        level = self.web_view.get_zoom_level()
        self.web_view.set_zoom_level(min(level + 0.1, 3.0))

    def zoom_out(self):
        level = self.web_view.get_zoom_level()
        self.web_view.set_zoom_level(max(level - 0.1, 0.5))

    def zoom_reset(self):
        self.web_view.set_zoom_level(1.0)

    def on_back_clicked(self, _):
        if self.web_view.can_go_back():
            self.web_view.go_back()

    def on_forward_clicked(self, _):
        if self.web_view.can_go_forward():
            self.web_view.go_forward()

    def on_reload_clicked(self, _):
        self.web_view.reload()

    def on_progress_changed(self, web_view, _):
        progress = web_view.get_estimated_load_progress()
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_visible(progress < 1.0)

    def on_title_changed(self, web_view, _):
        title = web_view.get_title()
        if title:
            self.title_widget.set_title(title)
            self.set_title(title)

    def on_uri_changed(self, web_view, _):
        uri = web_view.get_uri()
        if uri:
            try:
                from urllib.parse import urlparse
                host = urlparse(uri).netloc
                self.title_widget.set_subtitle(host if host else "chatgpt.com")
            except Exception:
                self.title_widget.set_subtitle("chatgpt.com")

    def on_load_changed(self, web_view, load_event):
        if load_event == WebKit.LoadEvent.FINISHED:
            self.progress_bar.set_visible(False)
            self.btn_back.set_sensitive(web_view.can_go_back())
            self.btn_forward.set_sensitive(web_view.can_go_forward())

    def on_create_popup(self, web_view, navigation_action):
        """Handle popup windows (such as Google OAuth or Apple Login)."""
        popup = Adw.Window(transient_for=self, modal=False)
        popup.set_default_size(520, 680)

        popup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        popup.set_content(popup_box)

        popup_header = Adw.HeaderBar()
        popup_header.add_css_class("flat")
        popup_title = Adw.WindowTitle(title="Login")
        popup_header.set_title_widget(popup_title)
        popup_box.append(popup_header)

        # Related view automatically inherits the parent view's network session
        popup_web_view = WebKit.WebView(related_view=web_view)
        popup_web_view.set_settings(self.settings)
        popup_web_view.set_vexpand(True)
        popup_web_view.set_hexpand(True)
        popup_box.append(popup_web_view)

        popup_web_view.connect(
            "notify::title",
            lambda wv, _: popup_title.set_title(wv.get_title() or "Login")
        )
        popup_web_view.connect("close", lambda _: popup.close())

        popup.present()
        return popup_web_view

    def on_permission_request(self, web_view, request):
        if isinstance(request, (WebKit.UserMediaPermissionRequest,
                                WebKit.DeviceInfoPermissionRequest,
                                WebKit.NotificationPermissionRequest)):
            request.allow()
            return True
        return False

    def on_close_request(self, _):
        width = self.get_width()
        height = self.get_height()
        is_max = self.is_maximized()
        save_window_state(width, height, is_max)
        return False


class ChatGPTApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_OPEN
        )
        self.win = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        self.setup_actions()

    def do_activate(self):
        if not self.win:
            self.win = ChatGPTWindow(self)
        self.win.present()

    def do_open(self, files, hint):
        self.do_activate()
        if files:
            for f in files:
                uri = f.get_uri()
                if uri and uri.startswith(("http://", "https://")):
                    self.win.web_view.load_uri(uri)
                    break

    def setup_actions(self):
        def add_action(name, callback):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)

        add_action("zoom_in", lambda *_: self.win.zoom_in() if self.win else None)
        add_action("zoom_out", lambda *_: self.win.zoom_out() if self.win else None)
        add_action("zoom_reset", lambda *_: self.win.zoom_reset() if self.win else None)
        add_action("inspect", self.action_inspect)
        add_action("copy_url", self.action_copy_url)
        add_action("clear_cache", self.action_clear_cache)
        add_action("about", self.action_about)
        add_action("quit", lambda *_: self.quit())

    def action_inspect(self, *_):
        if self.win:
            inspector = self.win.web_view.get_inspector()
            inspector.show()

    def action_copy_url(self, *_):
        if self.win:
            uri = self.win.web_view.get_uri()
            if uri:
                clipboard = Gdk.Display.get_default().get_clipboard()
                clipboard.set(uri)

    def action_clear_cache(self, *_):
        if self.win and self.win.session:
            dm = self.win.session.get_website_data_manager()
            dm.clear(WebKit.WebsiteDataTypes.MEMORY_CACHE | WebKit.WebsiteDataTypes.DISK_CACHE, 0, None, None)
            self.win.web_view.reload()

    def action_about(self, *_):
        about = Adw.AboutDialog(
            application_name="ChatGPT GTK",
            application_icon="chatgpt-gtk",
            developer_name="Galyarder",
            version="0.1.0",
            copyright="© 2026 Galyarder",
            comments="Lightweight, native GTK4/Libadwaita desktop client for ChatGPT web.",
            website="https://chatgpt.com",
            issue_url="https://github.com/galyarder/chatgpt-gtk"
        )
        about.present(self.win)


def main():
    app = ChatGPTApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
