/*
Copyright (C) 2015 Ericsson Canada Inc.
Licensed under the MIT license.

Created by William Sudletsky, 2015-04-07.

Flot plugin that allows a title to be added to the top of the graph, within the canvas.

The title will automatically find the edges of the grid and bound the title between them. The title will create line-breaks if necessary, and increase the top margin if margin is a margin object, or is null.

If the margin is a number, it will increase the margin for all sides.

Options are as follows:
options: {
        grid: {
                title: {
                        show: false,                    //Whether to show the title.
                        font: '12px sans-serif',        //The font of the title. ***IMPORTANT: SIZE OF FONT MUST BE IN PX, AND MUST BE THE FIRST NUMBER LISTED!***
                        color: 'black',                 //The colour of the text.
                        text: 'This is a Title',        //The actual contents of the title.
                        delimiter: ' ',                 //The string delimiter used to create line automatic line breaks.
                        interLineSpacing: 6             //The spacing, in pixels, between the top of the graph and the title, and between each line of text.
                }
        }
}
*/

(function ($) {
        var options = {
                grid: {
                        title: {
                                show: false,
                                font: '12px sans-serif',
                                color: 'black',
                                text: 'This is a Title',
                                delimiter: ' ',
                                interLineSpacing: 6
                        }
                }
        }

        /* 
        Init Function
        Adds the hooks to the plot and defines the functions
        */

        function init(plot) {

                /*
                addText Function

                Writes the text to the canvas, and wraps the text to be within maxWidth, using the delimtier and newline characters to split the string.

                Returns the distance between the font and the edge of the plot. The value is negative if the margin is too small, and the font is above the edge of the canvas.
                */

                function addText(context, text, x, y, maxWidth, spacing, delimiter, fontHeight) {
                        var words = text.split(/\r\n|\r|\n/g).map(function(value) {
                                return value.split(delimiter);
                                });
                        //alert(JSON.stringify(words));
                        var linesArray = [];
                        for(var i = 0; i < words.length; i++) {
                                var line_so_far = '';
                                for(var j = 0; j < words[i].length; j++) {
                                        var line = line_so_far + words[i][j] + delimiter;
                                        var measure = context.measureText(line);
                                        var lineWidth = measure.width;
                                        if (lineWidth > maxWidth && j > 0) {
                                                linesArray.push(line_so_far);
                                                line_so_far = words[i][j] + delimiter;
                                        } else {
                                            line_so_far = line;
                                        }
                                }
                                linesArray.push(line_so_far);
                        }
                        linesArray = linesArray.reverse();
                        for (var n = 0; n < linesArray.length; n++) {
                                context.fillText(linesArray[n], x, (y - ((spacing+maxHeight)*n)));
                        }
                        return (y - ((spacing+fontHeight)*(linesArray.length - 1))) - fontHeight;
                }

                /*
                triggerRedraw Function

                Only used wthin the bindEvents hook.

                First finds itself within bindEvents, and removes itself (as it only runs once), before causing the plot to redraw. The function is used for re-rendering the graph once the margins are altered.

                bindEvents is used as it is the last stage in building the plot.
                */

                function triggerRedraw(plot, eventHolder) {
                        var index = plot.hooks.bindEvents.indexOf(triggerRedraw);
                        plot.hooks.bindEvents.splice(index, 1);
                        plot.setupGrid();
                        plot.draw();
                }

                /*
                addPlotTitle Function

                The main function for this plugin.
                
                Sets the font options for the title, before passing the text and bounds to addText. The result from addText is used to determine whether to resize the margin or not. If the margin is resized, triggerRedraw is added to bindEvents.

                As the textAlign is changed to center for the title, it is changed back to left afterwards.
                */

                function addPlotTitle (plot, ctx) {

                        var options = plot.getOptions();

                        if (options.grid.title.show) {
                                var bounds = plot.getPlotOffset();
                                var canvas = plot.getCanvas();

                                ctx.font = options.grid.title.font;
                                ctx.fillStyle = options.grid.title.color;
                                ctx.textAlign = 'center';

                                var fontHeight = parseInt(ctx.font.match(/\d+/)[0]);

                                // The style width is required due to flot's auto-adjusting for different resolution displays.
                                var plotWidth = canvas.style.width.match(/\d+/)[0] - bounds.right - bounds.left;

                                var center = (plotWidth/2) + bounds.left;

                                try {
                                        var marginType = typeof options.grid.margin;
                                } catch(e) {
                                        var marginType = 'undefined';
                                }

                                if (marginType == 'string') {
                                        options.grid.margin = parseInt(options.grid.margin);
                                        marginType = 'number';
                                }

                                var heightAboveMargin = addText(ctx, options.grid.title.text, center, bounds.top - options.grid.title.interLineSpacing, plotWidth, options.grid.title.interLineSpacing, options.grid.title.delimiter, fontHeight)
                                if (heightAboveMargin < 0) {
                                        if (marginType == 'undefined') {
                                                options.grid.margin = {};
                                                options.grid.margin.top = (0 - heightAboveMargin + options.grid.title.interLineSpacing);
                                                plot.hooks.bindEvents.push(triggerRedraw);
                                        } else if (marginType == 'object') {
                                                if (options.grid.margin.hasOwnProperty('top')) {
                                                        options.grid.margin.top -= heightAboveMargin - options.grid.title.interLineSpacing;
                                                } else {
                                                        options.grid.margin.top = (0 - heightAboveMargin + options.grid.title.interLineSpacing);
                                                }
                                                plot.hooks.bindEvents.push(triggerRedraw);
                                        } else if (marginType == 'number') {
                                                options.grid.margin -= heightAboveMargin - options.grid.title.interLineSpacing;
                                                plot.hooks.bindEvents.push(triggerRedraw);
                                        }
                                }
                                ctx.textAlign = 'left';
                        }
                }

                /*
                * Adds hook to enable this plugin's logic shortly after drawing the whole graph
                */

                plot.hooks.draw.push(addPlotTitle);

        }
        $.plot.plugins.push({
                init: init,
                options: options,
                name: 'flot.addTitle',
                version: '0.1'
        });
})(jQuery);
