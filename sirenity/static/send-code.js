window.addEventListener('DOMContentLoaded', () => {
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

    const selectionObject = editor.getSession().getSelection();



    const themeSelect = document.querySelector('select#theme-select');
    const editorFontSize = document.querySelector('input#editor-font-size');
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



    let editorLineHeight = editor.getFontSize() * (7 / 6);

    // let charWidth= (editor.getFontSize / 2) * 1.1;//editor.getFontSize() / 2 + editor.getFontSize() / 20;

    // let gutterWidth = gutterElement.getBoundingClientRect().width//parseInt(gutterElement.style.width.slice(0, -2));

    editorFontSize.addEventListener('change', (e) => {
        if(editorFontSize.value > 50) {
            editorFontSize.value = 50;
        } else if(editorFontSize.value < 10) {
            editorFontSize.value = 10;
        }
        editor.setFontSize(editorFontSize.value + 'px');
        // editorLineHeight = editor.getFontSize() * (7 / 6);
        // charWidth= (editor.getFontSize / 2) * 1.1;
        // gutterWidth = gutterElement.getBoundingClientRect().width;
    });




    const otherCursors = {};
    const currentlyShowing = {};
    function addOtherCursor(pos, name) {
        let cursor;
        const {pageX, pageY} = editor.renderer.textToScreenCoordinates(pos.row, pos.column)
        if(!otherCursors.hasOwnProperty(name)){
            cursor = document.createElement('div');
            cursor.style.width = '1px';
            cursor.style.height = editorLineHeight + 'px';
            cursor.setAttribute('user-name', name);
            cursor.style.backgroundColor = 'red';
            cursor.style.position = 'absolute';
            cursor.classList.add('cursor');
            otherCursors[name] = cursor;
            document.body.appendChild(cursor);
        } else {
            cursor = otherCursors[name];
        }


        cursor.style.left = (
            pageX
            + 'px');
        cursor.style.top = (
            pageY
            +'px'
        );
        cursor.style.display= 'block';

        cursor.style.animation = 'disappear 1s linear';
        if(currentlyShowing.hasOwnProperty(name)) {
            currentlyShowing[name] += 1;
        } else {
            currentlyShowing[name] = 1;
        }
        setTimeout(() => {
            currentlyShowing[name] -= 1;
            if(currentlyShowing[name] == 0){
                delete currentlyShowing[name];
            } else {
                return
            }
            cursor.style.animation = '';
            cursor.style.display= 'none';
        }, 1000)
    }
    let userId, token;
    editor.addEventListener('change', (e) => {
        if (!(editor.curOp && editor.curOp.command.name)) return
        let a = editor.renderer.textToScreenCoordinates(e.end.row, e.end.column)
        websocket.send(JSON.stringify({
            data: {
                text: e.lines,
                start: e.start,
                end: e.end,
            },
            action: e.action,
            user_id: userId,
            token: token,
        }));
    });
    selectionObject.addEventListener('changeCursor', (e) => {
        websocket.send(JSON.stringify({
            data: {
                pos: selectionObject.getCursor(),
            },
            action: 'cursorMove',
            user_id: userId,
            token: token,
        }));
    });

    websocket.addEventListener('message', ({data}) => {
        data = JSON.parse(data);
        if(data.action == 'assign_id') {
            userId = data.user_id;
            token = data.token;
        } else {
            if(data.user_id == userId) return;
            editorDocument = editor.getSession().getDocument();
            editSession = editor.getSession();

            if(data.action == 'insert'){
                editorDocument.insertMergedLines(data.data.start, data.data.text);
                addOtherCursor(data.data.end, data.user_id);
            } else if (data.action == 'remove') {

                editorDocument.remove(new Range(
                    data.data.start.row,
                    data.data.start.column,
                    data.data.end.row,
                    data.data.end.column
                    )
                );
                addOtherCursor(data.data.start, data.user_id);
            } else if (data.action == 'cursorMove'){
                addOtherCursor(data.data.pos, data.user_id);
            } else {
                console.log('Unknown action: '+ data.action);
            }
        }
    });
});
