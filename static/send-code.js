window.addEventListener('DOMContentLoaded', () => {
    const websocket = new WebSocket(`ws://${window.location.host}/update-code`);
    var Range = require('ace/range').Range



    ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1");
    const editor = ace.edit('editor', {
        mode: "ace/mode/python",
        selectionStyle: "text"
    });
    const editorElement = document.getElementById("editor");
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

    const themeSelect = document.querySelector('select#theme-select');
    const editorFontSize = document.querySelector('input#editor-font-size');
    const editorFontSizeLabel = document.querySelector('label#editor-font-size-label');
    for(const theme of themes) {
        const node = document.createElement('option');
        if (theme == 'textmate'){
            node.selected = true;
        }
        node.value = `https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-${theme}.min.js`;
        node.text = theme;
        themeSelect.appendChild(node);
    }

    themeSelect.addEventListener('change', (e) => {
        const themeCDN = themeSelect.value;
        const theme = themeCDN.slice('https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-'.length, -('.min.js'.length));
        if(!themes.includes(theme)) return;

        editor.setTheme(`ace/theme/${theme}`);
    });




    const lineNumberLeftMargin = 20;
    let editorLineHeight = Math.round(editor.getFontSize() * (6 / 5));

    let charWidth= editor.getFontSize() / 2 + Math.round(editor.getFontSize() / 20);
    const lineNumberRightMargin= 12;
    const marginBetweenLineNumberAndText = 3;
    editorFontSize.addEventListener('change', (e) => {
        editor.setFontSize(editorFontSize.value + 'px');
        editorFontSizeLabel.innerText = editorFontSize.value + 'px';
        editorLineHeight = Math.round(editor.getFontSize() * (6 / 5));
        charWidth= editor.getFontSize() * 2 + Math.round(editor.getFontSize() / 20);
    });

    let userId;
    let typed = false;
    let focused = false;
    let receivedRemove = false;
    editor.addEventListener('change', (e) => {
        if((!typed || !focused) && (e.action != 'remove' || receivedRemove)) {
            return;
        }
        receivedRemove = false;

        websocket.send(JSON.stringify({
            text: e.lines,
            start: e.start,
            end: e.end,
            action: e.action,
            user_id: userId
        }));
    });

    function addOtherCursor(pos, name) {
        const cursor = document.createElement('div');
        cursor.style.width = '1px';
        cursor.style.height = editorLineHeight + 'px';
        cursor.setAttribute('user-name', name);
        cursor.style.backgroundColor = 'red';
        cursor.style.position = 'absolute';
        cursor.classList.add('cursor');
        let {left, top}= editorElement.getBoundingClientRect();
        cursor.style.left = (
            left
            + lineNumberLeftMargin
            + lineNumberRightMargin
            + (pos.row  +1) * charWidth  // Line number width
            + (pos.column + 1) * charWidth
            +marginBetweenLineNumberAndText
            + 'px');
        cursor.style.top = (
            top
            +pos.row * editorLineHeight
            +'px'
        );
        document.body.appendChild(cursor);
        setTimeout(() => {

            cursor.remove()
        }, 1000);
    }


    websocket.addEventListener('message', ({data}) => {
        data = JSON.parse(data);
        if(data.action == 'id') {
            userId = data.user_id;
        } else {
            if(data.user_id == userId) return;
            editorDocument = editor.getSession().getDocument();
            editSession = editor.getSession();

            if(data.action == 'insert'){
                editorDocument.insertMergedLines(data.start, data.text);
                addOtherCursor(data.end, data.user_id);
            } else if (data.action == 'remove') {

                receivedRemove = true;
                editorDocument.remove(new Range(
                    data.start.row,
                    data.start.column,
                    data.end.row,
                    data.end.column
                    )
                );
                addOtherCursor(data.end, data.user_id);
            } else {
                console.log('Unknown action: '+ data.action);
            }
        }
    });


    window.addEventListener('keydown', (e) => {
        typed = true;
    });


    window.addEventListener('keyup', (e) => {
        typed = false;
    });

    editor.addEventListener('focus', (e) => {
        focused = true;
    });

    editor.addEventListener('blur', (e) => {
        focused = false;
    });
});
