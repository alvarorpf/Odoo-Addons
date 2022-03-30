function drawGanttOnload()
{
    var g = new JSGantt.GanttChart(document.getElementById('GanttChartDIV'), 'day');
    g.setCaptionType('Complete'); // Set to Show Caption (None,Caption,Resource,Duration,Complete)
    g.setQuarterColWidth(36);
    g.setShowComp(0);
    g.setUseSort(0);
    g.setDateTaskDisplayFormat('day dd month yyyy'); // Shown in tool tip box
    g.setDayMajorDateDisplayFormat('mon yyyy - Week ww') // Set format to display dates in the "Major" header of the "Day" view
    g.setWeekMinorDateDisplayFormat('dd mon') // Set format to display dates in the "Minor" header of the "Week" view
    g.setShowTaskInfoLink(1); //Show link in tool tip (0/1)
    g.setShowEndWeekDate(0); // Show/Hide the date for the last day of the week in header for daily view(1/0)
    g.setUseSingleCell(10000); // Set the threshold at which we will only use one cell per table row (0disables). Helps with rendering performance for large charts.
    g.setFormatArr('Day', 'Week', 'Month', 'Quarter'); // Even with setUseSingleCell using Hour formation such a large chart can cause issues in some browsers
    g.setScrollTo('today')
    var project_id = document.getElementById('project_id').getAttribute('value');
    var tasks_table = document.getElementById('task_ids');
    var p_style = 'gtaskblue';
    var p_group = 0;
    var p_mile = 0;
    var date_end_gantt = '';
    for (var i = 0, row; row = tasks_table.rows[i]; i++)
    {
        var task_id = row.cells[0].firstElementChild.innerText;
        task_name = row.cells[1].firstElementChild.innerText;
        task_resp = row.cells[2].firstElementChild.innerText;
        var type = row.cells[3].firstElementChild.innerText;
        var date_start = row.cells[4].firstElementChild.innerText;
        var date_end = row.cells[5].firstElementChild.innerText;
        var date_deadline = row.cells[6].firstElementChild.innerText;
        var date_project_end = row.cells[7].firstElementChild.innerText;
        var macro_task = row.cells[8].firstElementChild.innerText;
        var description = row.cells[9].firstElementChild.innerText;
        var progress = row.cells[10].firstElementChild.innerText;
        var depend_task = row.cells[11].firstElementChild.innerText;
        if (type == 'Macro')
        {
            p_style = 'ggroupblack';
            p_group = 1;
            p_mile = 0;
        } else if (type == 'Developing')
        {
            p_style = 'ggroupblack';
            p_group = 0;
            p_mile = 0;
        } else {
            p_style = 'gtaskblue';
            p_group = 0;
            p_mile = 0;
        }
        date_end_gantt = date_end || date_deadline || date_project_end || '';
        // Parameters (pID, pName, pStart, pEnd, pStyle, pLink (unused) pMile, pRes, pComp, pGroup, pParent,pOpen, pDepend, pCaption, pNotes, pGantt)
        g.AddTaskItem(new JSGantt.TaskItem(task_id, task_name, date_start, date_end, p_style, '', p_mile,
        task_resp, progress, p_group, macro_task, 1, depend_task, '', description, g));
    }
    g.Draw();
}