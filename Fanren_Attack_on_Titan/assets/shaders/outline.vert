//Cg
// Outline vertex shader for Attack on Titan Fan Game
// Requirements: 8.1 - Anime-style outline effect

void vshader(
    float4 vtx_position : POSITION,
    float3 vtx_normal : NORMAL,
    
    out float4 l_position : POSITION,
    
    uniform float4x4 mat_modelproj,
    uniform float k_outline_width
)
{
    // Expand vertex along normal direction for outline
    float4 expanded_position = vtx_position;
    expanded_position.xyz += vtx_normal * k_outline_width;
    
    // Transform to clip space
    l_position = mul(mat_modelproj, expanded_position);
}
