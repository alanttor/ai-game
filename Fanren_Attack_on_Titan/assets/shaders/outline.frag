//Cg
// Outline fragment shader for Attack on Titan Fan Game
// Requirements: 8.1 - Anime-style outline effect

void fshader(
    out float4 o_color : COLOR,
    
    uniform float4 k_outline_color
)
{
    // Output solid outline color
    o_color = k_outline_color;
}
