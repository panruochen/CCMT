# YUNZ

This is a collection of misc tools

##### vimrc
<table>
  <tbody align="left">
    <tr>
      <th>Keymap</th>
      <th>Language</th>
      <th>Functions</th>
    </tr>
    <tr>
      <td>&lt;Normal&gt;%es</td>
      <td>all</td>
      <td>Expand leading tables to space within the whole file according to the value of TS</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;\es</td>
      <td>all</td>
      <td>Expand leading tables to space within selected lines according to the value of TS</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;\a</td>
      <td>all</td>
      <td>Align all columns for the selected lines.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\s</td>
      <td>all</td>
      <td><font color="blue">:s/\&lt;pattern\&gt;//</font></br> taking the current word as the pattern.</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;\s</td>
      <td>all</td>
      <td><font color="blue">&lt;,&gt;,:s/\&lt;pattern\&gt;//</font></br> taking the current word as the pattern.</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;<b>&lt;TAB&gt;</b></td>
      <td>all</td>
      <td>Add one tab at the front of every selected line.</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;<b>&lt;BACKSPACE&gt;</b></td>
      <td>all</td>
      <td>Remove one tab from the front of every selected line.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\u</td>
      <td>all</td>
      <td>Turn the word under the cursor to lower-case.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\U</td>
      <td>all</td>
      <td>Turn the word under the cursor to upper-case.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\]</td>
      <td>all</td>
      <td>Toggle line number display.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\[</td>
      <td>all</td>
      <td>Toggle relative line number display.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\n</td>
      <td>C/C++/H</td>
      <td>Select the entire function including the cursor.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\b</td>
      <td>C/C++/H</td>
      <td>Backward select the {} block including the cursor.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\f</td>
      <td>C/C++/H</td>
      <td>Forward select the {} block including the cursor.</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;\1</td>
      <td>C/C++/H</td>
      <td>Copy the first columns within the selected lines.</td>
    </tr>
    <tr>
      <td>&lt;Visual&gt;\2</td>
      <td>C/C++/H</td>
      <td>Copy the second columns within the selected lines.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;\x</td>
      <td>C/C++/H</td>
      <td>Paste a printf(...) statement according to columns copied by \1 or \2 beforehand.</td>
    </tr>
    <tr>
      <td>&lt;Normal&gt;<b>F9</b></td>
      <td>Make</td>
      <td>Select the $(...) block including the cursor.</td>
    </tr>
  </tbody>
</table>



