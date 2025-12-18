//Cg
// Cel-shading fragment shader for Attack on Titan Fan Game
// Requirements: 8.1 - Anime-style cel-shading visuals

void fshader(
    float2 l_texcoord0 : TEXCOORD0,
    float3 l_normal : TEXCOORD1,
    float3 l_world_position : TEXCOORD2,
    float3 l_view_direction : TEXCOORD3,
    
    out float4 o_color : COLOR,
    
    uniform sampler2D tex_0 : TEXUNIT0,
    uniform float4 p3d_LightDirection,
    uniform float4 k_ambient,
    uniform float4 k_diffuse,
    uniform float k_cel_levels,
    uniform float k_rim_power,
    uniform float4 k_rim_color
)
{
    // Sample base texture
    float4 base_color = tex2D(tex_0, l_texcoord0);
    
    // Normalize vectors
    float3 normal = normalize(l_normal);
    float3 light_dir = normalize(p3d_LightDirection.xyz);
    float3 view_dir = normalize(l_view_direction);
    
    // Calculate diffuse lighting with cel-shading quantization
    float ndotl = dot(normal, light_dir);
    float diffuse_intensity = max(0.0, ndotl);
    
    // Quantize to discrete levels for cel-shading effect
    float cel_levels = max(2.0, k_cel_levels);
    diffuse_intensity = floor(diffuse_intensity * cel_levels) / cel_levels;
    
    // Apply ambient and diffuse lighting
    float3 ambient = k_ambient.rgb * base_color.rgb;
    float3 diffuse = k_diffuse.rgb * base_color.rgb * diffuse_intensity;
    
    // Calculate rim lighting for anime-style edge highlight
    float rim = 1.0 - max(0.0, dot(view_dir, normal));
    rim = pow(rim, k_rim_power);
    float3 rim_light = k_rim_color.rgb * rim;
    
    // Combine all lighting components
    float3 final_color = ambient + diffuse + rim_light;
    
    o_color = float4(final_color, base_color.a);
}
