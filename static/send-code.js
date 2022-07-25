window.addEventListener('DOMContentLoaded', () => {
    const websocket = new WebSocket(`ws://${window.location.host}/update-code`);
    var Range = require('ace/range').Range



    ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1");
    const editor = ace.edit('editor', {
        mode: "ace/mode/python",
        selectionStyle: "text"
    });

    editor.setOptions({
        autoScrollEditorIntoView: true,
        copyWithEmptySelection: true,
    });

    const themes = [
        "ambiance",
        "chaos",
        "chrome",
        "cloud9_day",
        "cloud9_night",
        "cloud9_night_low_color",
        "clouds",
        "clouds_midnight",
        "cobalt",
        "crimson_editor",
        "dawn",
        "dracula",
        "dreamweaver",
        "eclipse",
        "github",
        "gob",
        "gruvbox",
        "gruvbox_dark_hard",
        "gruvbox_light_hard",
        "idle_fingers",
        "iplastic",
        "katzenmilch",
        "kr_theme",
        "kuroir",
        "merbivore",
        "merbivore_soft",
        "mono_industrial",
        "monokai",
        "nord_dark",
        "one_dark",
        "pastel_on_dark",
        "solarized_dark",
        "solarized_light",
        "sqlserver",
        "terminal",
        "textmate",
        "tomorrow",
        "tomorrow_night",
        "tomorrow_night_blue",
        "tomorrow_night_bright",
        "tomorrow_night_eighties",
        "twilight",
        "vibrant_ink",
        "xcode",
    ];

    const themeForm = document.querySelector('form#theme-form');
    const themeSelect = document.querySelector('select#theme-select');
    for(const theme of themes) {
        const node = document.createElement('option');
        if (theme == 'textmate'){
            node.selected = true;
        }
        node.value = `https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-${theme}.min.js`;
        node.text = theme;
        themeSelect.appendChild(node);
    }

    themeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const themeCDN = themeSelect.value;
        const theme = themeCDN.slice('https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-'.length, -('.min.js'.length));
        if(!themes.includes(theme)) return;

        editor.setTheme(`ace/theme/${theme}`);
    });



    // let cursorPos =
    editor.addEventListener('change', (e) => {
        websocket.send(JSON.stringify({
            text: e.lines,
            start: e.start,
            end: e.end,
            action: e.action,
        }));
    });
    websocket.addEventListener('message', ({data}) => {
        data = JSON.parse(data);
        editor_document = editor.getSession().getDocument();
        if(data.action == 'insert'){
            if(data.text == ['', '']) {
                editor_document.insertMergedLines(data.start, ['', '']);
            } else{
                editor_document.insert(data.start, data.text.join(''));
            }
        } else if (data.action == 'remove') {
            editor_document.remove(new Range(
                data.start.row,
                data.start.column,
                data.end.row,
                data.end.column
                )
            );
        } else {
            console.log('Unknown action: '+ data.action)
        }

    });

});
