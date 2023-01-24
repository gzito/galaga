#version 330 core

in  vec4 ex_color;
in  vec2 ex_tex_coords_0 ;

uniform sampler2D material_diffuse ;

out vec4 out_color;

void main(void)
{
	out_color = texture(material_diffuse, ex_tex_coords_0) * ex_color ;
}
