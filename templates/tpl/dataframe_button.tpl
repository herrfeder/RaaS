{# Update the template_structure.html document too #}
{%- block before_style -%}{%- endblock before_style -%}
{% block style %}
<style  type="text/css" >
{% block table_styles %}
{% for s in table_styles %}
    #T_{{uuid}} {{s.selector}} {
    {% for p,val in s.props %}
      {{p}}: {{val}};
    {% endfor -%}
    }
{%- endfor -%}
{% endblock table_styles %}
{% block before_cellstyle %}{% endblock before_cellstyle %}
{% block cellstyle %}
{%- for s in cellstyle %}
    #T_{{uuid}}{{s.selector}} {
    {% for p,val in s.props %}
        {{p}}: {{val}};
    {% endfor %}
    }
{%- endfor -%}
{%- endblock cellstyle %}
 th {background-color: #e7ebf6;}
 th:hover {background-color: #3D9970;} 
 tr:hover {background-color: #f5f5f5;} 
 tr {border-bottom: 1px solid #ddd;}
 td:hover {background-color: #F5D6C6;} 
</style>
{%- endblock style %}
{%- block before_table %}{% endblock before_table %}
{%- block table %}
<table id="table_leftiframe" {% if table_attributes %}{{ table_attributes }}{% endif %}>
{%- block caption %}
{%- if caption -%}
    <caption>{{caption}}</caption>
{%- endif -%}
{%- endblock caption %}
{%- block thead %}
<thead>
    {%- block before_head_rows %}{% endblock %}
    {%- for r in head %}
    {%- block head_tr scoped %}
    <tr>
        {%- for c in r %}
        {%- if c.is_visible != False %}
        <{{ c.type }} class="{{c.class}}" {{ c.attributes|join(" ") }} {%- if loop.index > 1 -%} value={{loop.index}} onclick="parent.hideshowCol(this)"{%- endif -%}>{{ c.value
}}</{{ c.type }}>
        {%- endif %}
        {%- endfor %}
    </tr>
    {%- endblock head_tr %}
    {%- endfor %}
    {%- block after_head_rows %}{% endblock %}
</thead>
{%- endblock thead %}
{%- block tbody %}
<tbody>
    {% block before_rows %}{% endblock before_rows %}
    {% for r in body %}
    {% block tr scoped %}
    <tr onclick="parent.get_dataframerow(this)">
        {% for c in r %}
        {% if c.is_visible != False %}
        <{{ c.type }} {% if c.id is defined -%} id="T_{{ c.id }}" {%- endif %} class="{{ c.class }} datafield" {{ c.attributes|join(" ") }}>{{ c.display_value }} 
	  <div class="btn-group-sm" id="datafieldbutton" role="group" aria-label="Basic example" style="display: None;">
	  	<button type="button" class="btn btn-secondary" value={{ c.display_value}} onclick="parent.send_filter('=',this)">=</button>
	  	<button type="button" class="btn btn-secondary" value={{ c.display_value}} onclick="parent.send_filter('<', this)">"<"</button>
	  	<button type="button" class="btn btn-secondary" value={{ c.display_value}}  onclick="parent.send_filter('>', this)">">"</button>
	  </div>
	</{{ c.type }}>
        {% endif %}
        {%- endfor %}
    <td><button>Action</button></td></tr>
    {% endblock tr %}
    {%- endfor %}
    {%- block after_rows %}{%- endblock after_rows %}
</tbody>
{%- endblock tbody %}
</table>
{%- endblock table %}
{%- block after_table %}{% endblock after_table %}
