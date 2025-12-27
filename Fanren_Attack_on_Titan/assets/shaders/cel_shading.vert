//Cg
// Cel-shading vertex shader for Attack on Titan Fan Game
// Requirements: 8.1 - Anime-style cel-shading visuals

void vshader(
    float4 vtx_position : POSITION,
    float3 vtx_normal : NORMAL,
    float2 vtx_texcoord0 : TEXCOORD0,
    
    out float4 l_position : POSITION,
    out float2 l_texcoord0 : TEXCOORD0,
    out float3 l_normal : TEXCOORD1,
    out float3 l_world_position : TEXCOORD2,
    out float3 l_view_direction : TEXCOORD3,
    
    uniform float4x4 mat_modelproj,
    uniform float4x4 mat_modelview,
    uniform float4 mspos_view
)
{
    // Transform vertex position to clip space
    l_position = mul(mat_modelproj, vtx_position);
    
    // Pass through texture coordinates
    l_texcoord0 = vtx_texcoord0;
    
    // Transform normal to view space
    l_normal = normalize(mul((float3x3)mat_modelview, vtx_normal));
    
    // Calculate world position for lighting
    float4 world_pos = mul(mat_modelview, vtx_position);
    l_world_position = world_pos.xyz;
    
    // Calculate view direction for specular
    l_view_direction = normalize(mspos_view.xyz - vtx_position.xyz);
}
